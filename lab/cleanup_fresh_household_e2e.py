import json,datetime
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
ROOT=Path(__file__).parent;out=ROOT.parent/'output/household-final-e2e'
states=[json.loads((out/name).read_text()) for name in ['workflow.json']];assert all(s['status']=='passed' for s in states)
ids=[s['id'] for s in states];intakes=ids[:];roots=[s['internal_id'] for s in states]
evidence={};counts={}
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT count(*) FROM g2p_intake_form_submissions s JOIN g2p_intake_form_households h ON h.submission_id=s.submission_id WHERE CAST(s.submission_id AS text)=ANY(%s) AND h.record_name LIKE %s',(intakes,'Meeting Verification%'))
  if q.fetchone()[0]!=len(intakes):raise RuntimeError('Fixture ownership check failed; no records removed')
  for table in ['g2p_register_individuals','g2p_register_household_assets']:
   q.execute(sql.SQL('SELECT internal_record_id FROM {} WHERE link_internal_record_id=ANY(%s)').format(sql.Identifier(table)),(roots,));roots += [r[0] for r in q.fetchall()]
import sqlite3,sys,yaml
from urllib.parse import quote
sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];session=login('https://g2p-odk.wverve.in','admin',password,True)
for state in states:
 with sqlite3.connect('/opt/openg2p-lab/odk-sync/ledger.sqlite') as ledger:
  ledger.execute("UPDATE imports SET state='EXCLUDED_TEST',error='Android acceptance verification complete; fixture removed.' WHERE instance_id=?",(state['instance'],));ledger.commit()
 response=session.delete('https://g2p-odk.wverve.in/v1/projects/1/forms/nsipa_registry_household/submissions/'+quote(state['instance'],safe=''),timeout=30)
 if response.status_code not in [200,404]:response.raise_for_status()
with connect('awe') as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute('SELECT * FROM approval_request WHERE artifact_id=ANY(%s)',(ids,));requests=q.fetchall();request_ids=[r['id'] for r in requests];evidence['approval_requests']=requests
  for table in ['approval_task','approval_decision','approval_event']:
   q.execute(sql.SQL('SELECT * FROM {} WHERE request_id=ANY(%s)').format(sql.Identifier(table)),(request_ids,));evidence[table]=q.fetchall()
  (out/'approval-fixture-evidence.json').write_text(json.dumps(evidence,default=str,indent=2))
  q.execute('DELETE FROM webhook_delivery WHERE event_id IN(SELECT id FROM approval_event WHERE request_id=ANY(%s))',(request_ids,));counts['webhooks']=q.rowcount
  q.execute('UPDATE approval_task SET decision_id=NULL WHERE request_id=ANY(%s)',(request_ids,))
  for table in ['approval_decision','approval_task','approval_event']:
   q.execute(sql.SQL('DELETE FROM {} WHERE request_id=ANY(%s)').format(sql.Identifier(table)),(request_ids,));counts[table]=q.rowcount
  q.execute('DELETE FROM approval_request WHERE id=ANY(%s)',(request_ids,));counts['approval_request']=q.rowcount
 c.commit()
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute('DELETE FROM g2p_registry_review_comments WHERE event_id IN(SELECT event_id FROM awe_req_events WHERE artifact_id=ANY(%s))',(ids,));counts['fixture_review_comments']=q.rowcount
  q.execute("SELECT t.tablename,c.column_name FROM pg_tables t JOIN information_schema.columns c ON c.table_schema=t.schemaname AND c.table_name=t.tablename WHERE t.schemaname='public' AND c.column_name=ANY(%s)",(['submission_id','change_request_id','internal_record_id','subject_internal_record_id','link_internal_record_id','artifact_id'],));tables={}
  for row in q.fetchall():tables.setdefault(row['tablename'],[]).append(row['column_name'])
  pending=[]
  for table,columns in tables.items():
   if not table.startswith(('g2p_','awe_req_','dedup_')):continue
   predicates=[];params=[]
   for column in columns:
    values=intakes if column=='submission_id' else ids if column in ['change_request_id','artifact_id'] else roots
    predicates.append(sql.SQL('CAST({} AS text)=ANY(%s)').format(sql.Identifier(column)));params.append(values)
   query=sql.SQL('DELETE FROM {} WHERE {}').format(sql.Identifier(table),sql.SQL(' OR ').join(predicates));pending.append((table,query,params))
  # Retry parents after their dependent fixture rows; unrelated rows are never selected.
  for _ in range(len(pending)+1):
   retry=[]
   for table,query,params in pending:
    q.execute('SAVEPOINT fixture_delete')
    try:q.execute(query,params);counts['register.'+table]=q.rowcount;q.execute('RELEASE SAVEPOINT fixture_delete')
    except Exception:q.execute('ROLLBACK TO SAVEPOINT fixture_delete');retry.append((table,query,params))
   if not retry:break
   if len(retry)==len(pending):raise RuntimeError('Fixture dependencies could not be resolved')
   pending=retry
 c.commit()

(out/'fixture-cleanup.json').write_text(json.dumps({'status':'completed','fixture_ids':ids,'original_records_selected':False,'removed_counts':counts},indent=2));print('Removed only the UUID-tracked mobile approval fixture; original records and sample draft retained.')
