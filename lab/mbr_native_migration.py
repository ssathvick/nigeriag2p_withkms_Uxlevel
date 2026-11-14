"""Lossless native/AWE migration. Existing records are linked, never approved or replayed."""
import argparse
import datetime as dt
import hashlib
import json
import re
import uuid
from collections import Counter
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import Json, RealDictCursor
from test_mbr_db_connection import connect

REGISTRY_ARTIFACTS = ('registry.intake_form', 'registry.change_request')
DDL = """
ALTER TABLE g2p_mbr_submissions ADD COLUMN IF NOT EXISTS title TEXT;
ALTER TABLE g2p_mbr_submissions ADD COLUMN IF NOT EXISTS native_origin TEXT;
ALTER TABLE g2p_mbr_submissions ADD COLUMN IF NOT EXISTS native_status TEXT;
DO $$ BEGIN
 IF EXISTS(SELECT 1 FROM pg_indexes WHERE schemaname=current_schema() AND indexname='g2p_mbr_open_change' AND indexdef NOT LIKE '%native_origin%') THEN
  EXECUTE 'DROP INDEX '||quote_ident(current_schema())||'.g2p_mbr_open_change';
  EXECUTE 'CREATE UNIQUE INDEX g2p_mbr_open_change ON '||quote_ident(current_schema())||'.g2p_mbr_submissions(master_id) WHERE kind=''change'' AND state IN (''DRAFT'',''RETURNED'',''PENDING'') AND native_origin IS DISTINCT FROM ''native''';
 END IF;
END $$;
ALTER TABLE g2p_mbr_events ADD COLUMN IF NOT EXISTS source_event_key TEXT;
ALTER TABLE g2p_mbr_events ADD COLUMN IF NOT EXISTS details JSONB;
CREATE UNIQUE INDEX IF NOT EXISTS g2p_mbr_history_source_key ON g2p_mbr_events(source_event_key);
CREATE TABLE IF NOT EXISTS g2p_mbr_source_archive (
 source_db TEXT NOT NULL,source_table TEXT NOT NULL,source_key TEXT NOT NULL,
 body JSONB NOT NULL,sha256 TEXT NOT NULL,captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 PRIMARY KEY(source_db,source_table,source_key));
CREATE TABLE IF NOT EXISTS g2p_mbr_native_map (
 submission_id UUID PRIMARY KEY REFERENCES g2p_mbr_submissions(id),
 native_kind TEXT NOT NULL,native_key TEXT NOT NULL,request_id TEXT,
 target_table TEXT,target_id TEXT,metadata JSONB NOT NULL,
 migrated_at TIMESTAMPTZ NOT NULL DEFAULT now(),UNIQUE(native_kind,native_key));
CREATE TABLE IF NOT EXISTS g2p_mbr_actor_alias (
 alias TEXT PRIMARY KEY,actor_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS g2p_mbr_migration_runs (
 id UUID PRIMARY KEY,report JSONB NOT NULL,created_at TIMESTAMPTZ NOT NULL DEFAULT now());
"""

def canonical(value):
    return json.dumps(value,default=str,sort_keys=True,separators=(',',':'))

def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()

def rows(cur,table):
    cur.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier(table)))
    return [json.loads(canonical(dict(x))) for x in cur.fetchall()]

def table_names(cur):
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=current_schema() ORDER BY table_name")
    return [x['table_name'] for x in cur.fetchall()]

def row_key(row):
    for key in ['history_record_id','event_id','id','change_request_id','submission_id']:
        if row.get(key):return str(row[key])
    return digest(row)

def archive(cur,db,table,records):
    # Include the complete row digest in the key for composite-key section tables.
    for row in records:
        cur.execute('''INSERT INTO g2p_mbr_source_archive(source_db,source_table,source_key,body,sha256)
         VALUES(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING''',
                    (db,table,row_key(row)+':'+digest(row),Json(row),digest(row)))

def normalize_state(native,request):
    status=(native.get('approval_status') or (request or {}).get('status') or 'PENDING').upper()
    if status in ['APPROVED','REJECTED']:return status
    if status in ['CANCELLED','CANCELED']:return 'CANCELLED'
    if status in ['RETURNED','RETURNED_FOR_CORRECTION']:return 'RETURNED'
    if native.get('draft_status')=='DRAFT':return 'DRAFT'
    if status in ['PENDING','IN_REVIEW','SUBMITTED']:return 'PENDING'
    raise ValueError('Unmapped native status: '+status)

def stable_uuid(value):
    try:return str(uuid.UUID(value))
    except ValueError:return str(uuid.uuid5(uuid.NAMESPACE_URL,'openg2p:native:'+value))

def normalize_intake(native,sections):
    household=next(iter(sections.get('g2p_intake_form_households',[])),{})
    people=sections.get('g2p_intake_form_individuals',[])
    members=[]
    for m in people:
        members.append({'id':m['internal_record_id'],'first_name':m.get('first_name') or m.get('given_name') or '',
                        'surname':m.get('last_name') or '', 'other_name':m.get('middle_name') or '',
                        'sex':str(m.get('gender') or '').title(),'age':m.get('estimated_age'),
                        'dob':m.get('birth_date'),'nin':m.get('foundational_id'),
                        'relationship':'Head of Household' if m['internal_record_id']==household.get('household_head_internal_record_id') else m.get('relationship_to_head')})
    return {'members':members,'assets':{},'shocks':[],'crops':[],
            'address':household.get('address_line_1'),'latitude':household.get('latitude'),'longitude':household.get('longitude'),
            'roof':household.get('roof_material'),'floor':household.get('floor_material'),'rooms':household.get('rooms_count'),
            'water':household.get('water_source_type'),'lighting':household.get('lighting_source'),'cooking_fuel':household.get('cooking_fuel_type'),
            'household_head_name':household.get('household_head_name'),'declared_household_size':household.get('size_total'),
            'legacy_sections':sections,'legacy_note':'Original native fields retained. Missing survey fields were not inferred.'}

def migrate(register_db='register',awe_db='awe',apply=False,guards=False):
    import mbr_workflow
    register=connect(register_db);awe=connect(awe_db)
    try:
        with register.cursor(cursor_factory=RealDictCursor) as cur, awe.cursor(cursor_factory=RealDictCursor) as ac:
            cur.execute('SELECT pg_advisory_xact_lock(73291411)')
            # Short locks produce one stable reconciliation boundary; no approval action is replayed.
            for table in ['approval_request','approval_task','approval_decision','approval_event']:
                ac.execute(sql.SQL('LOCK TABLE {} IN SHARE ROW EXCLUSIVE MODE').format(sql.Identifier(table)))
            names=table_names(cur)
            selected=[t for t in names if t.startswith(('g2p_intake_form_','g2p_register_history_')) or t in
                      ['g2p_register_change_requests','g2p_register_change_request_payloads','g2p_change_request_documents',
                       'g2p_intake_section_documents','awe_req_events','dedup_results_intake_forms_vs_intake_forms','dedup_results_intake_forms_vs_register','deduplication_change_request_results']]
            for table in selected:cur.execute(sql.SQL('LOCK TABLE {} IN SHARE ROW EXCLUSIVE MODE').format(sql.Identifier(table)))
            source={table:rows(cur,table) for table in selected}
            ac.execute('SELECT * FROM approval_request WHERE artifact_type=ANY(%s)',(list(REGISTRY_ARTIFACTS),))
            requests=[json.loads(canonical(dict(x))) for x in ac.fetchall()];request_ids=[x['id'] for x in requests]
            awe_source={'approval_request':requests}
            for table in ['approval_task','approval_decision','approval_event']:
                ac.execute(sql.SQL('SELECT * FROM {} WHERE request_id=ANY(%s)').format(sql.Identifier(table)),(request_ids,))
                awe_source[table]=[json.loads(canonical(dict(x))) for x in ac.fetchall()]
            before={t:digest(sorted(rs,key=canonical)) for t,rs in source.items()}
            cur.execute(mbr_workflow.SCHEMA);cur.execute(DDL)
            # The original state model has no cancelled value; retain cancellation explicitly.
            cur.execute('ALTER TABLE g2p_mbr_submissions DROP CONSTRAINT IF EXISTS g2p_mbr_submissions_state_check')
            cur.execute("ALTER TABLE g2p_mbr_submissions ADD CONSTRAINT g2p_mbr_submissions_state_check CHECK(state IN ('DRAFT','RETURNED','PENDING','REJECTED','APPROVED','CANCELLED'))")
            for table,rs in source.items():archive(cur,'register',table,rs)
            for table,rs in awe_source.items():archive(cur,'awe',table,rs)
            for database,tables in [('register',source),('awe',awe_source)]:
                for table,rs in tables.items():
                    cur.execute('SELECT sha256,count(*) n FROM g2p_mbr_source_archive WHERE source_db=%s AND source_table=%s GROUP BY sha256',(database,table))
                    archived={x['sha256']:x['n'] for x in cur.fetchall()}
                    if any(archived.get(key,0)<n for key,n in Counter(digest(x) for x in rs).items()):
                        raise ValueError('Archive row reconciliation failed for '+database+'.'+table)
            by_request={x['id']:x for x in requests}
            by_artifact={}
            for req in requests:by_artifact.setdefault(req['artifact_id'],[]).append(req)
            payloads={x['change_request_id']:x['change_payload'] for x in source['g2p_register_change_request_payloads']}
            cur.execute('SELECT register_id,register_mnemonic FROM g2p_register_definitions')
            mnemonics={x['register_id']:x['register_mnemonic'] for x in cur.fetchall()}
            created=0;existing=0;states=Counter();links=[];warnings=[]
            for kind,table,key in [('intake','g2p_intake_form_submissions','submission_id'),('change','g2p_register_change_requests','change_request_id')]:
                for native in source[table]:
                    native_id=native[key];sid=stable_uuid(native_id)
                    attempts=sorted(by_artifact.get(native_id,[]),key=lambda x:x['created_at'])
                    req=by_request.get(native.get('awe_request_id')) or (attempts[-1] if attempts else None)
                    stage=(req or {}).get('current_stage_order') or 1
                    if stage not in [1,2]:raise ValueError('Native request has an unsupported approval stage: '+str(stage))
                    state=normalize_state(native,req);states[state]+=1
                    sections={t:[x for x in rs if str(x.get('submission_id'))==native_id] for t,rs in source.items() if t.startswith('g2p_intake_form_') and t not in ['g2p_intake_form_submissions','g2p_intake_form_definitions','g2p_intake_form_ui_tabs','g2p_intake_form_ui_tab_sections']}
                    sections={t:rs for t,rs in sections.items() if rs}
                    target_table='g2p_register_households' if kind=='intake' else None
                    target_id=None;old=None;revision=None
                    if kind=='intake':
                        payload=normalize_intake(native,sections)
                        target_id=next(iter(sections.get('g2p_intake_form_households',[])),{}).get('internal_record_id')
                        title=payload.get('household_head_name') or next(iter(sections.get('g2p_intake_form_households',[])),{}).get('record_name')
                    else:
                        mnemonic=mnemonics[native['section_register_id']]
                        suffix=re.sub(r'(?<!^)(?=[A-Z])','_',mnemonic).lower()
                        target_table='g2p_register_'+({'household':'households','individual':'individuals'}.get(suffix,suffix))
                        if target_table not in names:raise ValueError('Cannot map native CR target '+mnemonic)
                        target_id=native['internal_record_id'];proposal=payloads.get(native_id)
                        payload={'members':[],'legacy_change_values':proposal,'legacy_note':'Original change payload; unavailable historical old values have not been reconstructed.'}
                        title=native.get('record_name')
                        cur.execute(sql.SQL('SELECT * FROM {} WHERE internal_record_id=%s').format(sql.Identifier(target_table)),(target_id,))
                        current=cur.fetchone()
                        if state not in ['APPROVED','REJECTED','CANCELLED'] and current:
                            old=json.loads(canonical(dict(current)));revision=digest(old)
                    date=native.get('first_created_at') or native.get('created_at')
                    reference=native.get('application_reference') or dt.datetime.fromisoformat(date).strftime('%Y%b%d').upper()+'-'+str(int(uuid.UUID(sid))%1000000).zfill(6)
                    decisions=[x for x in awe_source['approval_decision'] if req and x['request_id']==req['id'] and x['stage_order']==1 and x['action']=='approve']
                    level1=decisions[-1]['actor'] if decisions else None
                    metadata={'original':native,'attempt_ids':[x['id'] for x in attempts],
                              'migrated_stage':stage,
                              'tasks':[x for x in awe_source['approval_task'] if req and x['request_id']==req['id']],
                              'old_values_available':old is not None,'native_sections':sections,
                              'original_payload':payloads.get(native_id) if kind=='change' else None}
                    cur.execute('SELECT * FROM g2p_mbr_native_map WHERE native_kind=%s AND native_key=%s',(kind,native_id))
                    mapping=cur.fetchone()
                    if mapping:
                        if mapping['metadata'].get('native_current',mapping['metadata']['original'])!=native:raise ValueError('A migrated native source changed outside its owner: '+native_id)
                        existing+=1
                    else:
                        cur.execute('SELECT 1 FROM g2p_mbr_submissions WHERE id=%s OR reference=%s',(sid,reference))
                        if cur.fetchone():raise ValueError('Identity/reference collision; refusing to merge '+native_id)
                        cur.execute('''INSERT INTO g2p_mbr_submissions(id,reference,kind,state,stage,payload,old_payload,master_id,base_revision,
                         source,created_by,created_name,created_at,updated_at,reason,level1_actor,title,native_origin,native_status)
                         VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'native',%s)''',
                         (sid,reference,kind,state,stage,Json(payload),Json(old) if old is not None else None,target_id,revision,
                          native.get('submission_source') or native.get('change_request_source') or 'Native registry',native['created_by'],native['created_by'],
                          date,native.get('last_updated_at') or native.get('approved_at') or date,native.get('remarks'),level1,title,native['approval_status']))
                        cur.execute('INSERT INTO g2p_mbr_native_map(submission_id,native_kind,native_key,request_id,target_table,target_id,metadata) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                                    (sid,kind,native_id,native.get('awe_request_id'),target_table,target_id,Json(metadata)))
                        created+=1
                    links.append({'submission_id':sid,'native_key':native_id,'kind':kind,'state':state,'attempts':len(attempts)})
                    for event_type,rs in [('event',awe_source['approval_event']),('decision',awe_source['approval_decision'])]:
                        for e in rs:
                            if e['request_id'] not in metadata['attempt_ids']:continue
                            body=e.get('payload') or {}
                            actor=e.get('actor') or body.get('actor') or 'AWE system'
                            action=e.get('event_type') or (e.get('action','decision')+'_stage'+str(e.get('stage_order') or 1))
                            cur.execute('''INSERT INTO g2p_mbr_events(submission_id,actor,actor_name,action,comment,at,source_event_key,details)
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(source_event_key) DO NOTHING''',
                             (sid,actor,actor,action,e.get('comment') or body.get('comment') or '',e['created_at'],'awe:'+event_type+':'+e['id'],Json(e)))
            known={x['native_key'] for x in links}
            unmatched=[x['id'] for x in requests if x['artifact_id'] not in known]
            if unmatched:raise ValueError('Registry AWE requests have no native artifact; manual reconciliation required: '+','.join(unmatched))
            # Verify every byte-equivalent source row and every original ID/status before commit.
            unchanged={t:digest(sorted(rows(cur,t),key=canonical))==value for t,value in before.items()}
            if not all(unchanged.values()):raise ValueError('Migration altered native source rows')
            cur.execute("SELECT count(*) n FROM g2p_mbr_events WHERE source_event_key LIKE 'awe:%'");history=cur.fetchone()['n']
            report={'created':created,'already_migrated':existing,'native_records':len(links),'states':dict(states),'awe_requests':len(requests),
                    'awe_tasks':len(awe_source['approval_task']),'awe_decisions':len(awe_source['approval_decision']),
                    'awe_events':len(awe_source['approval_event']),'imported_history_entries':history,
                    'source_tables_unchanged':all(unchanged.values()),'archive_reconciled':True,'archived_native_rows':sum(len(rs) for rs in source.values()),'source_counts':{t:len(rs) for t,rs in source.items()},
                    'source_hashes':before,'links':links,'warnings':warnings,'scope':'Registry intake and change-request AWE artifacts; unrelated programme/payment approvals remain unchanged.'}
            cur.execute('INSERT INTO g2p_mbr_migration_runs(id,report) VALUES(%s,%s)',(str(uuid.uuid4()),Json(report)))
            if guards:
                install_native_guards(cur,selected)
                ac.execute(AWE_GUARD)
            if apply:
                # AWE guard commits first: if the registry commit fails, old decisions stay safely blocked until recovery.
                awe.commit();register.commit()
            else:register.rollback();awe.rollback()
            return report
    finally:register.close();awe.close()

AWE_GUARD='''
CREATE TABLE IF NOT EXISTS g2p_mbr_owned_requests(request_id TEXT PRIMARY KEY,migrated_at TIMESTAMPTZ NOT NULL DEFAULT now());
INSERT INTO g2p_mbr_owned_requests(request_id) SELECT id FROM approval_request WHERE artifact_type IN ('registry.intake_form','registry.change_request') ON CONFLICT DO NOTHING;
CREATE OR REPLACE FUNCTION g2p_mbr_owns_registry_decisions() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF EXISTS(SELECT 1 FROM approval_request WHERE id=NEW.request_id AND artifact_type IN ('registry.intake_form','registry.change_request'))
 THEN RAISE EXCEPTION 'Registry approvals moved to the integrated MBR workflow at /registration/mbr'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS g2p_mbr_decision_owner ON approval_decision;
CREATE TRIGGER g2p_mbr_decision_owner BEFORE INSERT ON approval_decision FOR EACH ROW EXECUTE FUNCTION g2p_mbr_owns_registry_decisions();
CREATE OR REPLACE FUNCTION g2p_mbr_freeze_owned_awe() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE request_key text;
BEGIN
 IF TG_TABLE_NAME='approval_request' THEN request_key=OLD.id; ELSE request_key=OLD.request_id; END IF;
 IF EXISTS(SELECT 1 FROM g2p_mbr_owned_requests WHERE request_id=request_key) THEN
  RAISE EXCEPTION 'This approval moved to the integrated MBR workflow at /registration/mbr';
 END IF;
 IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
END $$;
DROP TRIGGER IF EXISTS g2p_mbr_task_owner ON approval_task;
CREATE TRIGGER g2p_mbr_task_owner BEFORE UPDATE OR DELETE ON approval_task FOR EACH ROW EXECUTE FUNCTION g2p_mbr_freeze_owned_awe();
DROP TRIGGER IF EXISTS g2p_mbr_request_owner ON approval_request;
CREATE TRIGGER g2p_mbr_request_owner BEFORE UPDATE OR DELETE ON approval_request FOR EACH ROW EXECUTE FUNCTION g2p_mbr_freeze_owned_awe();
'''

def install_native_guards(cur,tables):
    cur.execute('''CREATE OR REPLACE FUNCTION g2p_mbr_native_write_guard() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE body jsonb; key text;
    BEGIN
     IF current_setting('g2p.mbr_writer',true)='on' THEN IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF; END IF;
     IF TG_OP='DELETE' THEN body=to_jsonb(OLD); ELSE body=to_jsonb(NEW); END IF;
     key=coalesce(body->>'submission_id',body->>'change_request_id');
     IF EXISTS(SELECT 1 FROM g2p_mbr_native_map WHERE native_key=key) THEN
      RAISE EXCEPTION 'This record is managed by the integrated MBR workflow at /registration/mbr';
     END IF;
     IF TG_TABLE_NAME IN ('g2p_intake_form_submissions','g2p_register_change_requests') AND TG_OP<>'DELETE'
      AND body->>'approval_status' IN ('APPROVED','REJECTED') THEN
      RAISE EXCEPTION 'Use the two-stage MBR approval workflow';
     END IF;
     IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
    END $$''')
    for table in tables:
        if table in ['g2p_intake_form_definitions','g2p_intake_form_ui_tabs','g2p_intake_form_ui_tab_sections'] or not table.startswith(('g2p_intake_form_','g2p_register_change_request')):continue
        cur.execute(sql.SQL('DROP TRIGGER IF EXISTS g2p_mbr_write_owner ON {}').format(sql.Identifier(table)))
        cur.execute(sql.SQL('CREATE TRIGGER g2p_mbr_write_owner BEFORE INSERT OR UPDATE OR DELETE ON {} FOR EACH ROW EXECUTE FUNCTION g2p_mbr_native_write_guard()').format(sql.Identifier(table)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--register-db',default='register');parser.add_argument('--awe-db',default='awe')
    parser.add_argument('--apply',action='store_true');parser.add_argument('--guards',action='store_true');parser.add_argument('--if-new',action='store_true');parser.add_argument('--report',required=True)
    args=parser.parse_args()
    if args.if_new:
        with connect(args.register_db) as c:
            with c.cursor() as cur:
                cur.execute("SELECT EXISTS(SELECT 1 FROM g2p_intake_form_submissions n WHERE NOT EXISTS(SELECT 1 FROM g2p_mbr_native_map m WHERE m.native_kind='intake' AND m.native_key=n.submission_id::text)) OR EXISTS(SELECT 1 FROM g2p_register_change_requests n WHERE NOT EXISTS(SELECT 1 FROM g2p_mbr_native_map m WHERE m.native_kind='change' AND m.native_key=n.change_request_id))")
                if not cur.fetchone()[0]:
                    print('{"status":"no_new_native_records"}')
                    raise SystemExit(0)
    result=migrate(args.register_db,args.awe_db,args.apply,args.guards)
    p=Path(args.report);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2));p.chmod(0o600)
    print(json.dumps({k:v for k,v in result.items() if k not in ['links','source_hashes','source_counts']}))
