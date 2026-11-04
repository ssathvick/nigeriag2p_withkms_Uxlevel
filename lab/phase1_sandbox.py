"""Isolated Phase 1 demonstrations. Never calls identity or payment providers."""
import datetime as dt
import json
import math
import sqlite3
import uuid
from pathlib import Path
from flask import Blueprint, abort, g, request, redirect, send_file

ROLES = {'iqs-intake-reviewer', 'iqs-programme-supervisor'}
CHANNELS = ('web', 'mobile', 'sms', 'ussd', 'call_centre', 'physical_desk')
REASONS = ('payment_delay', 'account_issue', 'registration_correction', 'service_quality')
LOCATIONS = [
    ('DEMO-HH-01', 'North Central', 'FCT', 'Bwari'),
    ('DEMO-HH-02', 'North East', 'Borno', 'Maiduguri'),
    ('DEMO-HH-03', 'North West', 'Kano', 'Dala'),
    ('DEMO-HH-04', 'South East', 'Enugu', 'Enugu North'),
    ('DEMO-HH-05', 'South South', 'Rivers', 'Port Harcourt'),
    ('DEMO-HH-06', 'South West', 'Lagos', 'Ikeja'),
]
TRANSLATIONS = {
    'en': ('Sandbox programme information', 'Demonstration only. No real payment or eligibility decision.', 'Household support', 'Programme information', 'Service locations', 'News', 'Public demonstration data'),
    'ha': ('Bayanin shirin gwaji', 'Wannan gwaji ne kawai. Babu biyan kuɗi na gaske ko yanke shawarar cancanta.', 'Tallafin iyali', 'Bayanin shiri', 'Wuraren hidima', 'Labarai', 'Bayanan gwaji na jama’a'),
    'yo': ('Àlàyé ètò ìdánwò', 'Ìdánwò nìkan ni èyí. Kò sí ìsanwó gidi tàbí ìpinnu ẹ̀tọ́ sí àǹfààní.', 'Ìrànlọ́wọ́ ìdílé', 'Àlàyé ètò', 'Àwọn ibi iṣẹ́', 'Ìròyìn', 'Dátà ìdánwò fún gbogbo ènìyàn'),
    'ig': ('Ozi mmemme nnwale', 'Nke a bụ naanị nnwale. Enweghị ịkwụ ụgwọ n’ezie ma ọ bụ mkpebi ntozu.', 'Nkwado ezinụlọ', 'Ozi mmemme', 'Ebe ọrụ', 'Akụkọ', 'Data nnwale ọha'),
}

def now():
    return dt.datetime.now(dt.timezone.utc)

def identifier(value):
    try:
        result = str(uuid.UUID(value))
    except (ValueError, TypeError, AttributeError):
        abort(400, 'Use a valid request identifier.')
    return result

def install(r):
    bp = Blueprint('phase1_sandbox', __name__)
    path = r.ROOT / 'phase1-sandbox.sqlite'
    def db():
        c = sqlite3.connect(path, timeout=30)
        c.row_factory = sqlite3.Row
        c.execute('PRAGMA journal_mode=WAL')
        return c
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS grievances(id TEXT PRIMARY KEY, request_id TEXT UNIQUE NOT NULL, actor TEXT NOT NULL, household TEXT NOT NULL, channel TEXT NOT NULL, reason TEXT NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL, created TEXT NOT NULL, response_due TEXT NOT NULL, resolution_due TEXT NOT NULL, responded TEXT, resolved TEXT);
        CREATE TABLE IF NOT EXISTS deliveries(id TEXT PRIMARY KEY, actor TEXT NOT NULL, household TEXT NOT NULL UNIQUE, payload TEXT NOT NULL, received TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, reference TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS agents(id TEXT PRIMARY KEY, household TEXT NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL, updated TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS phase1_agent_territory ON agents(household,state);
        CREATE INDEX IF NOT EXISTS phase1_case_owner ON grievances(actor,created);
        CREATE INDEX IF NOT EXISTS phase1_case_deadlines ON grievances(status,response_due,resolution_due);
        CREATE INDEX IF NOT EXISTS phase1_event_ref ON events(reference,id);
        ''')
        for ref,zone,state,lga in LOCATIONS:
            c.execute("INSERT OR IGNORE INTO agents VALUES(?,?,'onboarded',1,?)",('DEMO-AGENT-'+ref[-2:],ref,now().isoformat()))
    path.chmod(0o600)
    def require():
        r.require_user()
        if g.session.get('mode') != 'staff' or not ROLES.intersection(g.user.get('roles', [])):
            abort(403, 'An existing sandbox supervisor or reviewer account is required.')
    def event(c, ref, action):
        c.execute('INSERT INTO events(reference,actor,action,at) VALUES(?,?,?,?)', (ref, g.user['sub'], action, now().isoformat()))
    def reference(value):
        if value not in {x[0] for x in LOCATIONS}:
            abort(400, 'Choose a fictional demonstration household.')
        return value
    def tick():
        at=now().isoformat()
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            overdue=c.execute("SELECT * FROM grievances WHERE status IN ('open','acknowledged') AND ((responded IS NULL AND response_due<?) OR (resolved IS NULL AND resolution_due<?))",(at,at)).fetchall()
            for case in overdue:
                c.execute("UPDATE grievances SET status='escalated',version=version+1 WHERE id=?",(case['id'],))
                c.execute('INSERT INTO events(reference,actor,action,at) VALUES(?,?,?,?)',(case['id'],'system:sla','grievance_auto_escalated',at))
    def report():
        tick()
        with db() as c:
            cases = [dict(x) for x in c.execute('SELECT * FROM grievances ORDER BY created DESC LIMIT 200')]
            for x in cases:
                x.pop('actor'); x.pop('request_id')
                x['response_overdue'] = x['responded'] is None and dt.datetime.fromisoformat(x['response_due']) < now()
                x['resolution_overdue'] = x['resolved'] is None and dt.datetime.fromisoformat(x['resolution_due']) < now()
            deliveries = [{**json.loads(x['payload']), 'received': x['received']} for x in c.execute('SELECT * FROM deliveries ORDER BY received DESC LIMIT 200')]
            events = [dict(x) for x in c.execute('SELECT reference,action,at FROM events ORDER BY id DESC LIMIT 50')]
            agents=[dict(x) for x in c.execute('SELECT * FROM agents ORDER BY id LIMIT 200')]
            agent_counts={x[0]:x[1] for x in c.execute('SELECT state,COUNT(*) FROM agents GROUP BY state')}
        return {'synthetic': True, 'grievances': cases, 'deliveries': deliveries, 'events': events,'agents':agents,'agent_counts':agent_counts,'agent_total':sum(agent_counts.values())}
    @bp.get(r.PREFIX+'/phase1')
    def console():
        if not g.user:
            return redirect(r.PREFIX+'/login?mode=staff&phase1=1')
        require()
        return r.page('phase1.html', report=report(), locations=LOCATIONS, channels=CHANNELS, reasons=REASONS, request_id=str(uuid.uuid4()))
    @bp.get(r.PREFIX+'/api/phase1/report')
    def api_report():
        require(); return report()
    @bp.get(r.PREFIX+'/api/phase1/context')
    def field_context():
        require(); return {'csrf': g.session['csrf'], 'synthetic': True}
    @bp.get(r.PREFIX+'/phase1/grievances')
    def my_cases():
        if not g.user:return redirect(r.PREFIX+'/login?grievances=1')
        if g.session.get('mode')=='staff':return redirect(r.PREFIX+'/phase1#grievances')
        if g.session.get('mode')!='beneficiary':abort(403)
        profile=r.one('SELECT household_ref FROM profiles WHERE sub=?',(g.user['sub'],))
        with db() as c:cases=[dict(x) for x in c.execute('SELECT id,household,reason,status,created,response_due,resolution_due FROM grievances WHERE actor=? ORDER BY created DESC LIMIT 200',(g.user['sub'],))]
        return r.page('phase1-grievances.html',cases=cases,profile=profile,reasons=REASONS,request_id=str(uuid.uuid4()))
    @bp.post(r.PREFIX+'/phase1/agents/<aid>/<action>')
    def agent_action(aid,action):
        require()
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            agent=c.execute('SELECT * FROM agents WHERE id=?',(aid,)).fetchone()
            if not agent:abort(404,'Agent not found.')
            if request.form.get('version')!=str(agent['version']):abort(409,'Agent changed; refresh before updating.')
            transition={'train':('onboarded','trained'),'certify':('trained','certified'),'revoke':('certified','revoked')}.get(action)
            if not transition or agent['state']!=transition[0]:abort(409,'Complete the preceding training/certification stage first.')
            c.execute('UPDATE agents SET state=?,version=version+1,updated=? WHERE id=?',(transition[1],now().isoformat(),aid))
            event(c,aid,'agent_'+action)
        return redirect(r.PREFIX+'/phase1#agents')
    @bp.post(r.PREFIX+'/phase1/grievances')
    def create_case():
        r.require_user()
        citizen=g.session.get('mode')=='beneficiary'
        if not citizen:require()
        key = identifier(request.form.get('request_id'))
        if citizen:
            profile=r.one('SELECT household_ref FROM profiles WHERE sub=?',(g.user['sub'],))
            if not profile:abort(409,'Register a fictional household before creating a case.')
            household=profile['household_ref']
            if request.form.get('household')!=household:abort(403,'Only your own household can be used for a case.')
        else:household = reference(request.form.get('household'))
        channel, reason = request.form.get('channel'), request.form.get('reason')
        if citizen and channel not in ('web','mobile'):abort(403,'Citizens can submit web or mobile cases only.')
        if channel not in CHANNELS or reason not in REASONS:
            abort(400, 'Choose a supported channel and issue.')
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            previous = c.execute('SELECT * FROM grievances WHERE request_id=?', (key,)).fetchone()
            if previous:
                if (previous['actor'], previous['household'], previous['channel'], previous['reason']) != (g.user['sub'],household,channel,reason):
                    abort(409, 'This request identifier already belongs to another submission.')
                return redirect(r.PREFIX+'/phase1/grievances' if citizen else r.PREFIX+'/phase1#grievances')
            if c.execute('SELECT COUNT(*) FROM grievances').fetchone()[0] >= 10000:
                abort(409, 'Sandbox capacity reached; contact the administrator.')
            at = now(); cid = 'DEMO-GRM-'+uuid.uuid4().hex[:12]
            c.execute('INSERT INTO grievances VALUES(?,?,?,?,?,?,?,1,?,?,?,NULL,NULL)', (cid,key,g.user['sub'],household,channel,reason,'open',at.isoformat(),(at+dt.timedelta(hours=48)).isoformat(),(at+dt.timedelta(days=14)).isoformat()))
            event(c,cid,'grievance_created')
        return redirect(r.PREFIX+'/phase1/grievances' if citizen else r.PREFIX+'/phase1#grievances')
    @bp.post(r.PREFIX+'/phase1/grievances/<cid>/<action>')
    def update_case(cid, action):
        require()
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            case = c.execute('SELECT * FROM grievances WHERE id=?', (cid,)).fetchone()
            if not case: abort(404, 'Case not found.')
            if request.form.get('version') != str(case['version']): abort(409, 'The case changed. Reload before deciding.')
            states = {'acknowledge': ('open','acknowledged'), 'escalate': ('acknowledged','escalated'), 'resolve': ('acknowledged','resolved')}
            if action == 'resolve' and case['status'] == 'escalated': expected, status = 'escalated','resolved'
            else: expected,status = states.get(action,(None,None))
            if case['status'] != expected: abort(409, 'This action is not available for the current case status.')
            at=now().isoformat()
            c.execute('UPDATE grievances SET status=?,version=version+1,responded=COALESCE(responded,?),resolved=? WHERE id=?', (status,at,at if status=='resolved' else None,cid))
            event(c,cid,'grievance_'+action)
        return redirect(r.PREFIX+'/phase1#grievances')
    @bp.get(r.PREFIX+'/phase1/field')
    def field():
        require()
        # Offline shell intentionally has no session, user or CSRF data.
        return r.app.make_response(__import__('flask').render_template('phase1-field.html',locations=LOCATIONS,prefix=r.PREFIX))
    @bp.get(r.PREFIX+'/phase1/field/sw.js')
    def worker():
        response=send_file(r.ROOT/'static/phase1-sw.js',mimetype='application/javascript',max_age=0)
        response.headers['Service-Worker-Allowed']=r.PREFIX+'/phase1/field'
        return response
    @bp.post(r.PREFIX+'/api/phase1/deliveries')
    def sync_delivery():
        require()
        rid=identifier(request.form.get('id')); household=reference(request.form.get('household'))
        if request.form.get('biometric') != 'mock_match': abort(400,'A successful mock biometric check is required.')
        try:
            lat, lon, accuracy = (float(request.form.get(k,'')) for k in ('latitude','longitude','accuracy_m'))
            captured=dt.datetime.fromisoformat(request.form.get('captured','').replace('Z','+00:00'))
            if captured.tzinfo is None or captured > now()+dt.timedelta(minutes=5): raise ValueError()
            if not all(math.isfinite(x) for x in (lat,lon,accuracy)) or not -90<=lat<=90 or not -180<=lon<=180 or not 0<=accuracy<=10: raise ValueError()
        except (ValueError,TypeError): abort(400,'Check coordinates, reported accuracy and capture timestamp.')
        payload={'id':rid,'household':household,'latitude':lat,'longitude':lon,'accuracy_m':accuracy,'captured':captured.isoformat(),'biometric':'mock_match','synthetic':True}
        encoded=json.dumps(payload,sort_keys=True)
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT * FROM deliveries WHERE id=?',(rid,)).fetchone()
            if old:
                if old['actor']!=g.user['sub'] or old['payload']!=encoded: abort(409,'This delivery identifier has conflicting details.')
                return {'accepted':False,'duplicate':True,'id':rid,'synthetic':True}
            if c.execute('SELECT id FROM deliveries WHERE household=?',(household,)).fetchone(): abort(409,'This demonstration household already has delivery proof.')
            agent=c.execute('SELECT * FROM agents WHERE household=?',(household,)).fetchone()
            if not agent or agent['state']!='certified':abort(409,'Certify the fictional agent for this household territory before synchronising.')
            c.execute('INSERT INTO deliveries VALUES(?,?,?,?,?)',(rid,g.user['sub'],household,encoded,now().isoformat()))
            event(c,rid,'delivery_synced')
        return {'accepted':True,'duplicate':False,'id':rid,'synthetic':True}
    r.app.register_blueprint(bp)
    import phase1_cms
    phase1_cms.install(r,db,LOCATIONS)
    import phase1_observability
    phase1_observability.install(r,db)
    import phase1_conditionality
    phase1_conditionality.install(r,db,LOCATIONS)
    r.phase1_db=db
    r.phase1_tick=tick
    @r.app.after_request
    def phase1_headers(response):
        if request.path.startswith(r.PREFIX+'/phase1') or request.path.startswith(r.PREFIX+'/api/phase1'):
            response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; worker-src 'self'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
            response.headers['Permissions-Policy']='camera=(), microphone=()'
        return response
