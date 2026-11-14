"""Reconciliation, idempotency and transition checks against restored databases only."""
import datetime as dt,json,types,uuid
from flask import Flask,g,request
from werkzeug.exceptions import HTTPException
from psycopg2 import sql
from psycopg2.extras import Json,RealDictCursor
from test_mbr_db_connection import connect
from mbr_native_migration import migrate,rows,digest,canonical,AWE_GUARD
import mbr_workflow

import sys
register_db,awe_db=sys.argv[1:3]
assert register_db.startswith('mbr_rehearsal_') and awe_db.startswith('mbr_rehearsal_')
checks=0
def check(value,label):
 global checks
 assert value,label
 checks+=1
with connect(register_db) as c,connect(awe_db) as a:
 with c.cursor(cursor_factory=RealDictCursor) as cur,a.cursor(cursor_factory=RealDictCursor) as ac:
  masters={t:digest(sorted(rows(cur,t),key=canonical)) for t in ['g2p_register_households','g2p_register_individuals']}
  ac.execute("SELECT * FROM approval_request WHERE artifact_type NOT IN ('registry.intake_form','registry.change_request')")
  unrelated=digest(sorted([dict(x) for x in ac.fetchall()],key=canonical))
result=migrate(register_db,awe_db,True,True)
check(result['created']==0 and result['already_migrated']==32,'Idempotent rerun')
check(result['awe_requests']==37 and result['awe_tasks']==71,'Request and assignment counts')
check(result['awe_decisions']==69 and result['awe_events']==214 and result['imported_history_entries']==283,'History reconciled')
check(result['source_tables_unchanged'],'Source hashes unchanged')
with connect(register_db) as c,connect(awe_db) as a:
 with c.cursor(cursor_factory=RealDictCursor) as cur,a.cursor(cursor_factory=RealDictCursor) as ac:
  for table,expected in masters.items():check(digest(sorted(rows(cur,table),key=canonical))==expected,'No master replay '+table)
  ac.execute("SELECT * FROM approval_request WHERE artifact_type NOT IN ('registry.intake_form','registry.change_request')")
  check(digest(sorted([dict(x) for x in ac.fetchall()],key=canonical))==unrelated,'Unrelated AWE records unchanged')
  cur.execute("SELECT count(*) n FROM g2p_mbr_submissions WHERE native_origin='native' AND state='APPROVED'");check(cur.fetchone()['n']==32,'Native statuses preserved')
  cur.execute("SELECT count(*) n FROM g2p_mbr_native_map WHERE jsonb_array_length(metadata->'attempt_ids')>1");check(cur.fetchone()['n']==5,'Five rejected/resubmitted histories linked to original intakes')
  cur.execute("SELECT count(*) n FROM g2p_mbr_submissions m JOIN g2p_intake_form_submissions n ON m.id=n.submission_id WHERE m.reference=n.application_reference AND m.created_by=n.created_by AND m.created_at AT TIME ZONE 'UTC'=n.first_created_at")
  check(cur.fetchone()['n']==30,'Native UUIDs, references, authors and original timestamps preserved')
  cur.execute("SELECT count(*) n FROM g2p_mbr_source_archive WHERE source_table LIKE 'g2p_register_history_%'");check(cur.fetchone()['n']>0,'Native version history archived')
  cur.execute("SELECT submission_id FROM g2p_intake_form_submissions LIMIT 1");protected=cur.fetchone()['submission_id']
try:
 with connect(register_db) as c:
  with c.cursor() as cur:cur.execute('UPDATE g2p_intake_form_submissions SET remarks=%s WHERE submission_id=%s',('unauthorized legacy write',protected))
 raise AssertionError('Native mutation guard allowed legacy write')
except Exception as e:check('integrated MBR workflow' in str(e),'Old native mutation rejected')
with connect(awe_db) as c:
 with c.cursor(cursor_factory=RealDictCursor) as cur:
  cur.execute("SELECT d.* FROM approval_decision d JOIN approval_request r ON r.id=d.request_id WHERE r.artifact_type='registry.intake_form' LIMIT 1");decision=dict(cur.fetchone())
try:
 with connect(awe_db) as c:
  with c.cursor() as cur:
   decision['id']=str(uuid.uuid4())
   cur.execute(sql.SQL('INSERT INTO approval_decision ({}) VALUES ({})').format(sql.SQL(',').join(map(sql.Identifier,decision)),sql.SQL(',').join(sql.Placeholder() for _ in decision)),list(decision.values()))
 raise AssertionError('Old AWE decision allowed')
except Exception as e:check('integrated MBR workflow' in str(e),'Old AWE approval rejected')

# A disposable Stage 2 native CR verifies that migration does not reset or replay Stage 1.
cid=str(uuid.uuid4());rid=str(uuid.uuid4());taskid=str(uuid.uuid4());now=dt.datetime.now(dt.timezone.utc)
with connect(register_db) as c,connect(awe_db) as a:
 with c.cursor(cursor_factory=RealDictCursor) as cur,a.cursor(cursor_factory=RealDictCursor) as ac:
  cur.execute("SELECT * FROM g2p_register_change_requests WHERE section_register_id='a0000000-0000-4000-8000-000000000002' LIMIT 1");cr=dict(cur.fetchone())
  cr.update(change_request_id=cid,approval_status='PENDING',awe_request_id=rid,created_at=now,approved_at=None,approved_by=None,remarks=None)
  cur.execute("SELECT set_config('g2p.mbr_writer','on',true)")
  def add(cursor,table,data):
   cursor.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,data)),sql.SQL(',').join(sql.Placeholder() for _ in data)),[Json(v) if isinstance(v,(dict,list)) else v for v in data.values()])
  add(cur,'g2p_register_change_requests',cr)
  add(cur,'g2p_register_change_request_payloads',{'change_request_id':cid,'change_payload':[{'internal_record_id':cr['internal_record_id'],'edit_action':'UPDATE','address_line_1':'Rehearsal Stage 2 correction'}],'search_text':'Rehearsal'})
  ac.execute("SELECT * FROM approval_request WHERE artifact_type='registry.change_request' LIMIT 1");req=dict(ac.fetchone())
  req.update(id=rid,artifact_id=cid,status='in_review',current_stage_order=2,created_at=now,updated_at=now,completed_at=None)
  add(ac,'approval_request',req)
  ac.execute('SELECT * FROM approval_task WHERE request_id=%s AND stage_order=2 LIMIT 1',(decision['request_id'],));task=ac.fetchone()
  if not task:
   ac.execute('SELECT * FROM approval_task WHERE stage_order=2 LIMIT 1');task=ac.fetchone()
  task=dict(task);task.update(id=taskid,request_id=rid,stage_order=2,assignee='reviewer-two',status='open',decision_id=None,completed_at=None,created_at=now,updated_at=now)
  add(ac,'approval_task',task)
  ac.execute('ALTER TABLE approval_decision DISABLE TRIGGER g2p_mbr_decision_owner')
  ac.execute('SELECT * FROM approval_decision LIMIT 1');first=dict(ac.fetchone())
  first.update(id=str(uuid.uuid4()),request_id=rid,task_id=taskid,stage_order=1,actor='first-reviewer',action='approve',comment='Preserved first-stage approval',created_at=now,updated_at=now)
  add(ac,'approval_decision',first)
  ac.execute('ALTER TABLE approval_decision ENABLE TRIGGER g2p_mbr_decision_owner')
result=migrate(register_db,awe_db,True,True);check(result['created']==1,'Pending source imported without changing status')
with connect(register_db) as c:
 with c.cursor() as cur:cur.execute("INSERT INTO g2p_mbr_actor_alias(alias,actor_id) VALUES('reviewer-two','second-reviewer') ON CONFLICT DO NOTHING")
app=Flask(__name__)
@app.before_request
def context():
 g.user={'sub':request.headers.get('X-Actor','second-reviewer'),'roles':[request.headers.get('X-Role','mbr-level2')],'name':'Rehearsal reviewer'};g.session={'mode':'staff'}
@app.errorhandler(HTTPException)
def error(e):return {'error':e.description},e.code
r=types.SimpleNamespace(app=app,PREFIX='/registration',pg=lambda name:connect(register_db if name=='register' else awe_db),require_user=lambda:None,
                       stamp=lambda:dt.datetime.now(dt.timezone.utc).isoformat(),redirect=lambda x:x,page=lambda *a,**kw:'MBR')
mbr_workflow.install(r);client=app.test_client()
url='/registration/mbr/api/submissions/'+cid
data=client.get(url).get_json();check(data['stage']==2 and data['state']=='PENDING','Stage 2 position retained')
check(any(e['comment']=='Preserved first-stage approval' for e in data['events']),'First-stage decision retained')
check(data['migration']['tasks'][0]['assignee']=='reviewer-two','Task assignee retained')
check(data['migration']['old_values_available'],'Pending change has real pre-change snapshot')
response=client.post(url+'/decision',data={'payload':json.dumps({'action':'approve','version':data['version']})},headers={'X-Actor':'first-reviewer'})
check(response.status_code==403,'Prior reviewer cannot approve again')
response=client.post(url+'/decision',data={'payload':json.dumps({'action':'approve','version':data['version']})})
check(response.status_code==200 and response.get_json()['state']=='APPROVED','Migrated Stage 2 approval succeeds once')
with connect(register_db) as c:
 with c.cursor() as cur:
  cur.execute('SELECT address_line_1 FROM g2p_register_households WHERE internal_record_id=%s',(cr['internal_record_id'],));check(cur.fetchone()[0]=='Rehearsal Stage 2 correction','Native CR applies to original record')
  cur.execute('SELECT approval_status FROM g2p_register_change_requests WHERE change_request_id=%s',(cid,));check(cur.fetchone()[0]=='APPROVED','Native CR status mirrored atomically')
  cur.execute('SELECT count(*) FROM g2p_register_history_households WHERE change_request_id=%s',(cid,));check(cur.fetchone()[0]==1,'New native version recorded once')
response=client.post(url+'/decision',data={'payload':json.dumps({'action':'approve','version':data['version']})})
check(response.status_code==409,'Approval retry cannot replay change')
result=migrate(register_db,awe_db,True,True);check(result['created']==0,'Rerun respects new workflow-owned state')
print(json.dumps({'checks':checks,'result':'passed','historical_records':32,'historical_awe_requests':37,'historical_history_entries':283,'fixture_database':register_db}))
