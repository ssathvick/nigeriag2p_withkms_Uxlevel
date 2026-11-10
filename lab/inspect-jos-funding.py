import sys,json,subprocess
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('bridge_db') as c:
 with c.cursor() as q:
  q.execute("SELECT column_name FROM information_schema.columns WHERE table_name='envelope_batch_status_for_cash'");print('columns',[v[0] for v in q.fetchall()])
  q.execute("SELECT row_to_json(t) FROM envelope_batch_status_for_cash t WHERE disbursement_envelope_id='e6cdb549-9502-42f8-88c5-4a8d2cd70392'");print(q.fetchall())
logs=subprocess.check_output(['kubectl','-n','nigeria','logs','deploy/bridge-celery-worker','--tail=120'],text=True)
print('\n'.join(line for line in logs.splitlines() if any(v in line.lower() for v in ['error','failed','e6cdb549','jos','funds','exception']))[-7000:])
