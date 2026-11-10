import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
evidence=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence');sid=json.loads((evidence/'native-statement-upload.json').read_text())['statement_id']
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute('SELECT statement_process_status FROM account_statements WHERE statement_id=%s',(sid,));status=cur.fetchone()[0]
if status!='PROCESSED':
 code="from openg2p_g2p_bridge_celery_workers.app import Initializer\nInitializer()\nfrom openg2p_g2p_bridge_celery_workers.tasks.mt940_processor import mt940_processor_worker\nmt940_processor_worker.run("+repr(sid)+")\n"
 run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/bridge-celery-worker','--','python','-'],input=code,capture_output=True,text=True,timeout=60)
 p=r.ROOT/'phase1-private-tests/native-statement-processor.log';p.write_text(run.stdout+run.stderr);p.chmod(0o600)
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute('SELECT statement_process_status,statement_process_error_code FROM account_statements WHERE statement_id=%s',(sid,));status,error=cur.fetchone()
  cur.execute('SELECT COUNT(DISTINCT disbursement_id) FROM disbursement_recons WHERE disbursement_id IS NOT NULL');reconciled=cur.fetchone()[0]
  cur.execute('SELECT COUNT(*) FROM disbursement_error_recons');errors=cur.fetchone()[0]
report={'scope':'Local native Example Bank MT940 and native Bridge reconciliation','statement_id':sid,'statement_status':status,'processor_error':error,'reconciled_instructions':reconciled,'exception_entries':errors,'status':'passed' if status=='PROCESSED' and reconciled==6 and errors==0 else 'failed'}
(evidence/'native-reconciliation-uat.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
