import json
import test_meeting_native_workflow as t
from test_mbr_db_connection import connect
path=t.OUT/'native-collect-state.json';case=json.loads(path.read_text())
def save():path.write_text(json.dumps(case,indent=2))
if not case.get('level1'):
 t.decide(case,'abutu@gmail.com','approve','Full offline interview completeness and duplicate review.')
 t.wait_for(lambda:any(task['stage_order']==2 and task['status']=='open' for task in t.tasks(case)),'Offline second review');t.check('Offline first approval leaves master unpublished',not t.master(case));case['level1']=True;save()
if not case.get('approved'):
 t.decide(case,'adaku@gmail.com','approve','Independent approval of offline household, roster and assets.',stage=2)
 t.wait_for(lambda:t.master(case),'Offline native publication');case['approved']=True;save()
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT size_total,monthly_household_income,health_insurance_status FROM g2p_register_households WHERE internal_record_id=%s',(case['internal_id'],));assert q.fetchone()==(2,12000,'NO')
  q.execute('SELECT count(*) FROM g2p_register_individuals WHERE link_internal_record_id=%s',(case['internal_id'],));assert q.fetchone()[0]==2
  q.execute('SELECT count(*) FROM g2p_register_household_assets WHERE link_internal_record_id=%s',(case['internal_id'],));assert q.fetchone()[0]==1
t.check('Offline final approval publishes household, repeat members and assets into native master')
