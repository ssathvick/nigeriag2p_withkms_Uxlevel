import json
from pathlib import Path
from test_mbr_db_connection import connect
state=json.loads((Path(__file__).parent.parent/'output/ooru-meeting-audit/verification/enumeration-sample.json').read_text());assert state['sample'] is True
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT internal_record_id FROM g2p_intake_form_households WHERE submission_id=%s',(state['submission_id'],));rows=q.fetchall();assert len(rows)==1
  q.execute("UPDATE g2p_intake_form_households SET record_name='SAMPLE — Household enumeration walkthrough',household_head_name='Sample Household Head',household_heads_count=1,head_list_complete='YES',size_total=1 WHERE submission_id=%s",(state['submission_id'],))
  q.execute("UPDATE g2p_intake_form_individuals SET link_internal_record_id=%s WHERE submission_id=%s AND first_name='Sample' AND last_name='Household Head'",(rows[0][0],state['submission_id']));assert q.rowcount==1
 c.commit()
print('Restored the known sample labels and its member link; no original records selected')
