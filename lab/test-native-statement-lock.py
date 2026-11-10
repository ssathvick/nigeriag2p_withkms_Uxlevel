"""Verify installed native MT940 guard while another DB connection holds its lock."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute("SELECT statement_id FROM account_statements WHERE statement_process_status='PROCESSED' ORDER BY created_at DESC LIMIT 1");sid=cur.fetchone()[0]
  cur.execute('SELECT COUNT(*) FROM disbursement_recons');before=cur.fetchone()[0]
  cur.execute('SELECT pg_try_advisory_lock(hashtextextended(%s,0))',('phase1-mt940:'+sid,));assert cur.fetchone()[0]
  try:
   code='''from openg2p_g2p_bridge_celery_workers.app import Initializer
Initializer()
from openg2p_g2p_bridge_celery_workers.tasks.mt940_processor import statement_processing_lock,mt940_processor_worker
with statement_processing_lock(SID) as acquired:
 assert acquired is False
mt940_processor_worker.run(SID)
print('PHASE1_CONCURRENT_RECEIPT_SKIPPED')
'''.replace('SID',repr(sid))
   run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/bridge-celery-worker','--','python','-'],input=code,text=True,capture_output=True,timeout=60)
   p=r.ROOT/'phase1-private-tests/statement-lock.log';p.write_text(run.stdout+run.stderr);p.chmod(0o600);assert run.returncode==0
  finally:cur.execute('SELECT pg_advisory_unlock(hashtextextended(%s,0))',('phase1-mt940:'+sid,))
  cur.execute('SELECT COUNT(*) FROM disbursement_recons');after=cur.fetchone()[0]
report={'scope':'Installed native worker and actual PostgreSQL per-statement concurrency lock','another_connection_rejected':True,'reconciliation_count_preserved':before==after,'status':'passed' if before==after else 'failed','limitation':'A completed fixture; large pending-statement failure recovery remains to be workload tested.'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-statement-lock.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
