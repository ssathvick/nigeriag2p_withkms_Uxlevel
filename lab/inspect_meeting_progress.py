from pathlib import Path
import json,sys
from test_mbr_db_connection import connect
state=json.loads((Path(__file__).parent.parent/'output/ooru-meeting-audit/verification/native-workflow-state.json').read_text())
with connect() as c:
 with c.cursor() as q:
  for case in state['cases'].values():
   q.execute('SELECT draft_status,approval_status,awe_request_id,awe_request_status_summary FROM g2p_intake_form_submissions WHERE submission_id=%s',(case['id'],));print('native',q.fetchone())
   q.execute('SELECT event_type,applied,error FROM awe_req_events WHERE artifact_id=%s ORDER BY received_at DESC LIMIT 4',(case['id'],));print('native callbacks',q.fetchall())
with connect('awe') as c:
 with c.cursor() as q:
  for case in state['cases'].values():
   if '--retry' in sys.argv:
    q.execute("UPDATE webhook_delivery SET next_attempt_at=now() WHERE status='pending' AND event_id IN(SELECT e.id FROM approval_event e JOIN approval_request r ON r.id=e.request_id WHERE r.artifact_id=%s)",(case['id'],));c.commit()
   q.execute('SELECT id,status FROM approval_request WHERE artifact_id=%s',(case['id'],));print('awe',q.fetchall())
   q.execute('SELECT e.event_type,d.status,d.last_error FROM webhook_delivery d JOIN approval_event e ON e.id=d.event_id JOIN approval_request r ON r.id=e.request_id WHERE r.artifact_id=%s ORDER BY e.created_at DESC LIMIT 4',(case['id'],));print('deliveries',q.fetchall())
