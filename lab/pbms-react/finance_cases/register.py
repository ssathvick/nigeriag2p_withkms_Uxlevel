"""Programme-scoped PBMS case register. Case decisions never dispatch funds."""
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import uuid
from contextlib import closing

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import jsonify, request, send_file

HERE = Path(__file__).parent
STORE = Path(os.environ.get('STATE_DIRECTORY', '/var/lib/pbms-finance')) / 'cases.sqlite'
UTC = dt.timezone.utc
def encode(value):
    return json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)

def connect():
    con = sqlite3.connect(STORE, timeout=12)
    con.row_factory = sqlite3.Row
    return con

def initialize():
    with closing(connect()) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS cases(
          ref TEXT PRIMARY KEY, list_id INTEGER NOT NULL, instruction TEXT NOT NULL,
          state TEXT NOT NULL, version INTEGER NOT NULL, outcome TEXT, recorder INTEGER,
          UNIQUE(list_id,instruction));
        CREATE TABLE IF NOT EXISTS events(
          case_ref TEXT NOT NULL, version INTEGER NOT NULL, actor INTEGER NOT NULL,
          name TEXT NOT NULL, at TEXT NOT NULL, action TEXT NOT NULL, note TEXT NOT NULL,
          snapshot TEXT NOT NULL, request_id TEXT NOT NULL, PRIMARY KEY(case_ref, version),
          UNIQUE(actor,request_id));
        """)

def install(app, User, Problem):
    initialize()
    def fail(message, code=400):
        raise Problem(message, code)
    def identity():
        user = User()
        who = user.call('g2p.beneficiary.list','nsipa_identity')
        roles = set()
        if who.get('payment'): roles.add('Payment')
        if 'Finance' in who.get('roles',[]): roles.add('Finance')
        if not roles: fail('Payment or Finance access is required.',403)
        return user,who,roles
    def binding(user, list_id):
        row, prog = user.listing(list_id)
        if not prog['nsipa_flow'] or row['list_stage'] != 'disbursement' or not row['nsipa_payment_hash']:
            fail('Select a submitted NSIPA disbursement list.',409)
        wid = user.wizard(row,prog)
        envs = user.call('g2p.api.disbursement.envelope.line','search_read',
                         [[['wizard_id','=',wid]]],{'fields':['disbursement_envelope_id','number_of_beneficiaries','total_disbursement_quantity','measurement_unit']})
        details = user.call('g2p.beneficiary.list','read',[[list_id]],{'fields':['nsipa_revision']})[0]
        return dict(program=prog['program_mnemonic'], list_id=list_id, revision=details['nsipa_revision'],
                    envelopes=[e['disbursement_envelope_id'] for e in envs], envelope_totals=envs, approval_hash=row['nsipa_payment_hash'])
    def evidence(user,list_id,as_of=None):
        ctx = binding(user,list_id)
        now=dt.datetime.now(UTC)
        try: cutoff=dt.datetime.fromisoformat(as_of.replace('Z','+00:00')) if as_of else now
        except (ValueError,AttributeError):fail('Use an ISO timestamp with a UTC offset.')
        if cutoff.tzinfo is None or cutoff>now:fail('Choose a past timestamp with a UTC offset.')
        cutoff=cutoff.astimezone(UTC).replace(tzinfo=None)
        approved=user.call('nsipa.approval.line','search_read',
                           [[['list_id','=',list_id],['included','=',True]]],{'fields':['beneficiary_id','amount']})
        amounts={x['beneficiary_id']:x['amount'] for x in approved}
        with closing(psycopg2.connect(os.environ['FINANCE_EVIDENCE_DSN'],connect_timeout=5)) as pg:
            pg.set_session(readonly=True)
            with pg.cursor(cursor_factory=RealDictCursor) as q:
                q.execute("""SELECT * FROM pbms_finance.instructions WHERE envelope=ANY(%s) AND issued_at<=%s
                             ORDER BY instruction""",(ctx['envelopes'],cutoff));rows=q.fetchall()
                q.execute("""SELECT * FROM pbms_finance.entries WHERE instruction=ANY(%s) AND processed_at<=%s
                             ORDER BY processed_at,receipt,entry_number""",([r['instruction'] for r in rows],cutoff))
                entries={}
                for item in q.fetchall():
                    item=dict(item);item['amount']=str(item['amount']);entries.setdefault(item.pop('instruction'),[]).append(item)
        for r in rows:
            r['approved_amount']=amounts.get(r.pop('beneficiary_id'))
            r['entries']=entries.get(r['instruction'],[])
            def match(entry,directions,receipt):
                return (entry['direction'] in directions and entry['receipt']==receipt and entry['currency']==r['currency']
                        and r['approved_amount'] is not None and float(entry['amount'])==r['approved_amount']==r['issued_amount'])
            credit=any(match(e,('C','D'),r['remittance']) for e in r['entries'])
            reversed_=any(match(e,('RC','RD'),r['reversal']) for e in r['entries'])
            r['supported']='Reversed' if credit and reversed_ else 'Reconciled' if credit else 'Pending'
            r['amount_exception']=any(e['currency']!=r['currency'] or float(e['amount'])!=r['approved_amount'] for e in r['entries'])
            # Historical views expose only receipts available at the selected time.
            visible={e['receipt'] for e in r['entries']}
            for k in ('remittance','reversal'):
                if r[k] not in visible:r[k]=None
        return {**ctx,'as_of_utc':cutoff.isoformat()+'Z','rows':rows}
    def case_detail(con,ref):
        r=con.execute('SELECT * FROM cases WHERE ref=?',(ref,)).fetchone()
        if not r:fail('No case in this list.',404)
        events=[]
        for e in con.execute('SELECT version,name,actor,at,action,note,snapshot FROM events WHERE case_ref=? ORDER BY version',(ref,)):
            events.append({**dict(e),'snapshot':json.loads(e['snapshot'])})
        return {**dict(r),'events':events}
    @app.get('/pbms-ui-api/finance-register')
    def register_page():return send_file(HERE/'register.html')
    @app.post('/pbms-ui-api/finance-register/queue')
    def queue():
        u,who,roles=identity()
        with closing(connect()) as c:
            lists=[r[0] for r in c.execute('SELECT DISTINCT list_id FROM cases')]
            allowed=u.call('g2p.beneficiary.list','search',[[['id','in',lists],['program_id.nsipa_flow','=',True]]]) if lists else []
            cases=[dict(r) for r in c.execute('SELECT * FROM cases ORDER BY rowid DESC') if r['list_id'] in allowed]
        return jsonify(name=who['name'],roles=sorted(roles),cases=cases)
    @app.post('/pbms-ui-api/finance-register/<int:list_id>')
    def operate(list_id):
        u,who,roles=identity();p=request.get_json()
        if not isinstance(p,dict):fail('Invalid request.')
        act=p.get('action','lookup');ref=p.get('ref','')
        data=evidence(u,list_id,p.get('as_of') or None)
        if act=='lookup':
            if p.get('instruction'):
                data['rows']=[r for r in data['rows'] if r['instruction']==p['instruction']]
                if not data['rows']:fail('No matching instruction in this list at the selected time.',404)
            return app.response_class(encode(data),mimetype='application/json')
        uid=who['uid']
        with closing(connect()) as c, c:
            if act=='read':
                row=c.execute('SELECT ref FROM cases WHERE ref=? AND list_id=?',(ref,list_id)).fetchone()
                if not row:fail('No case in this list.',404)
                return jsonify(case_detail(c,ref))
            if act not in ('create','send','acknowledge','record','review','close','note'):fail('Unknown case action.')
            needed='Payment' if act in ('create','send') else 'Finance'
            if needed not in roles:fail(needed+' role required.',403)
            note=p.get('note','')
            if not isinstance(note,str) or not 3<=len(note.strip())<=1500:fail('Enter a note of 3 to 1500 characters.')
            try:rid=str(uuid.UUID(p.get('request_id','')))
            except (ValueError,TypeError,AttributeError):fail('A request ID is required.')
            c.execute('BEGIN IMMEDIATE')
            retry=c.execute('SELECT case_ref,action FROM events WHERE actor=? AND request_id=?',(uid,rid)).fetchone()
            if retry:
                old=case_detail(c,retry['case_ref'])
                if old['list_id']!=list_id or retry['action']!=act or (ref and old['ref']!=ref):fail('Request ID already used.',409)
                return jsonify(old)
            if act=='create':
                instruction=p.get('instruction','')
                if not any(r['instruction']==instruction for r in data['rows']):fail('Choose an instruction from this list.',404)
                if c.execute('SELECT 1 FROM cases WHERE list_id=? AND instruction=?',(list_id,instruction)).fetchone():
                    fail('A case already exists for this instruction. Open it in the case register.',409)
                ref='FIN-'+uuid.uuid4().hex[:16].upper()
                c.execute("INSERT INTO cases VALUES(?,?,?,'Open',0,NULL,NULL)",(ref,list_id,instruction))
            case=c.execute('SELECT * FROM cases WHERE ref=? AND list_id=?',(ref,list_id)).fetchone()
            if not case:fail('No case in this list.',404)
            allowed={'create':('Open',),'send':('Open',),'acknowledge':('Sent to Finance',),'record':('Acknowledged','Recorded','Reviewed'),'review':('Recorded',),'close':('Reviewed',),'note':('Closed',)}
            if case['state'] not in allowed[act] or (act!='create' and case['version']!=p.get('version')):
                fail('Case changed. Reload before continuing.',409)
            target=next((r for r in data['rows'] if r['instruction']==case['instruction']),None)
            if not target:fail('Instruction unavailable at this time.',409)
            if case['version']:
                previous=json.loads(c.execute('SELECT snapshot FROM events WHERE case_ref=? AND version=?',
                                              (ref,case['version'])).fetchone()[0])
                if dt.datetime.fromisoformat(data['as_of_utc'].replace('Z','+00:00')) < dt.datetime.fromisoformat(previous['as_of_utc'].replace('Z','+00:00')):
                    fail('Choose an evidence cutoff at or after the preceding case event.',409)
            state={'create':'Open','send':'Sent to Finance','acknowledge':'Acknowledged','record':'Recorded',
                   'review':'Reviewed','close':'Closed','note':'Closed'}[act]
            outcome=case['outcome'];recorder=case['recorder']
            if act=='acknowledge' and c.execute('SELECT actor FROM events WHERE case_ref=? AND action=?',(ref,'send')).fetchone()[0]==uid:
                fail('A different Finance recipient must acknowledge the handoff.',403)
            if act=='record':
                outcome=p.get('outcome')
                if outcome not in ('Pending',target['supported']):fail('Selected outcome lacks matching statement evidence.',409)
                recorder=uid
            if act in ('review','close') and outcome!='Pending' and outcome!=target['supported']:
                fail('New evidence changes the outcome. Record an amendment before review or closure.',409)
            if act=='review' and uid==recorder:fail('A different Finance reviewer must check the outcome.',403)
            if act=='close' and outcome=='Pending':fail('Resolve the pending instruction before closure.',409)
            snap={k:v for k,v in data.items() if k!='rows'};snap['evidence']=target;snap['outcome']=outcome
            if act=='note':
                receipt=p.get('receipt');candidates=[e for e in target['entries'] if e['receipt']==receipt and (p.get('entry') is None or e['entry_number']==p.get('entry'))]
                selected=candidates[0] if len(candidates)==1 else None
                if not selected:fail('Select the later bank receipt from the instruction.',409)
                earlier=json.loads(c.execute("SELECT snapshot FROM events WHERE case_ref=? AND action='close'",(ref,)).fetchone()[0])
                for old in c.execute("SELECT snapshot FROM events WHERE case_ref=? AND action='note'",(ref,)):
                    old_snapshot=json.loads(old[0])
                    if old_snapshot.get('later_receipt')==receipt and old_snapshot.get('later_entry',selected['entry_number'])==selected['entry_number']:
                        fail('This receipt already has a case annotation.',409)
                prior=earlier['evidence']['entries']
                if any(e['receipt']==receipt for e in prior) or selected['processed_at'].replace(tzinfo=UTC)<=dt.datetime.fromisoformat(earlier['as_of_utc'].replace('Z','+00:00')):fail('Choose bank evidence later than the closure evidence cutoff.',409)
                keys=('direction','amount','currency','bank_ref','movement_date')
                snap['later_receipt']=receipt;snap['later_entry']=selected['entry_number']
                snap['comparison']='Repeated bank movement' if any(all(selected[k]==e[k] for k in keys) for e in prior) else 'Different or unverified movement; refer for decision'
            version=case['version']+1
            c.execute('UPDATE cases SET state=?,version=?,outcome=?,recorder=? WHERE ref=?',(state,version,outcome,recorder,ref))
            c.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?)',(ref,version,uid,who['name'],dt.datetime.now(UTC).isoformat(),act,note.strip(),encode(snap),rid))
            return jsonify(case_detail(c,ref))
