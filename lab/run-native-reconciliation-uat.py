"""Generate a native Example Bank statement and record actual reconciliation counts."""
import datetime as dt,json,sys,time
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
output=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-reconciliation-uat.json')
response=requests.post(r.svc('openg2p-g2p-bridge-example-bank-api')+'/generate_account_statement',json={'program_account_number':'PHASE1-DEMO-TREASURY'},timeout=10);response.raise_for_status()
report={'scope':'Six existing fictional payments in local native Example Bank','statement_requested':response.json().get('status'),'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
for _ in range(24):
 with r.pg('bridge_db') as c:
  with c.cursor() as cur:
   cur.execute('SELECT COUNT(DISTINCT disbursement_id) FROM disbursement_recons WHERE disbursement_id IS NOT NULL');reconciled=cur.fetchone()[0]
   cur.execute('SELECT statement_process_status,COUNT(*) FROM account_statements GROUP BY statement_process_status');states=[list(x) for x in cur.fetchall()]
 report.update(reconciled_instructions=reconciled,statement_states=states)
 output.write_text(json.dumps(report,indent=2))
 if reconciled==6:break
 time.sleep(5)
report['status']='passed' if reconciled==6 else 'blocked';report['finished_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
output.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
