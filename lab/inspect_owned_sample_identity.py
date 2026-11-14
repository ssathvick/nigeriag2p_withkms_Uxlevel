import json
from pathlib import Path
from test_mbr_db_connection import connect
s=json.loads((Path(__file__).parent.parent/'output/ooru-meeting-audit/verification/enumeration-sample.json').read_text())
with connect() as c:
 with c.cursor() as q:q.execute('SELECT internal_record_id,record_name,household_head_name FROM g2p_intake_form_households WHERE submission_id=%s',(s['submission_id'],));print(q.fetchall())
