import json
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
report=json.loads(Path('/opt/openg2p-lab/registration/mbr-migration-inspection.json').read_text())
for db,table in [('register','g2p_register_change_requests'),('register','g2p_register_change_request_payloads'),('awe','approval_request'),('awe','approval_decision')]:
 print(db,table,json.dumps(report[db][table]['samples'],default=str))
for db,queries in {'register':["SELECT approval_status,draft_status,count(*) FROM g2p_intake_form_submissions GROUP BY 1,2", "SELECT approval_status,count(*) FROM g2p_register_change_requests GROUP BY 1", "SELECT submission_id,application_reference,created_by,approval_status,draft_status,awe_request_id,register_ingest_process_status FROM g2p_intake_form_submissions ORDER BY first_created_at", "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%payload%' OR table_name LIKE '%member%')"], 'awe':["SELECT artifact_type,status,current_stage_order,count(*) FROM approval_request GROUP BY 1,2,3", "SELECT r.id,r.artifact_type,r.artifact_id,r.status,r.current_stage_order,t.assignee,t.stage_order,t.status FROM approval_request r LEFT JOIN approval_task t ON r.id=t.request_id WHERE r.status NOT IN ('approved','rejected','cancelled')", "SELECT event_type,count(*) FROM approval_event GROUP BY 1", "SELECT action,count(*) FROM approval_decision GROUP BY 1"]}.items():
 with connect(db) as c:
  with c.cursor() as cur:
   for q in queries:cur.execute(q);print(db,q,cur.fetchall())
