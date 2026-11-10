"""Run installed worker methods on existing synthetic records; never forge success states."""
import datetime as dt,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  if '--household' in sys.argv:
   cur.execute("SELECT b.id,b.disbursement_envelope_id FROM disbursement_batch_control b JOIN disbursement_envelopes e ON e.id=b.disbursement_envelope_id WHERE e.benefit_program_mnemonic='IQS_INTEGRATED_HOUSEHOLD_SUPPORT' AND e.disbursement_cycle_id=4 AND EXISTS(SELECT 1 FROM disbursements d WHERE d.disbursement_batch_control_id=b.id AND d.beneficiary_id='IQS-REG-HH-9300745d55295cdb')")
   batches=cur.fetchall();assert len(batches)==1;batch,envelope=batches[0]
  else:
   cur.execute('SELECT id,disbursement_envelope_id FROM disbursement_batch_control ORDER BY created_at LIMIT 1');batch,envelope=cur.fetchone()
code='''
from urllib.parse import urlparse
from openg2p_g2p_bridge_celery_workers.app import Initializer
Initializer()
from openg2p_g2p_bridge_bank_connectors.config import Settings
config=Settings.get_config()
assert all(urlparse(getattr(config,key)).hostname=='openg2p-g2p-bridge-example-bank-api' for key in ['funds_available_check_url_example_bank','funds_block_url_example_bank','funds_disbursement_url_example_bank'])
from openg2p_g2p_bridge_celery_workers.tasks.mapper_resolution_task import mapper_resolution_worker
from openg2p_g2p_bridge_celery_workers.tasks.check_funds_with_bank import check_funds_with_bank_worker
from openg2p_g2p_bridge_celery_workers.tasks.block_funds_with_bank import block_funds_with_bank_worker
from openg2p_g2p_bridge_celery_workers.tasks.disburse_funds_from_bank import disburse_funds_from_bank_worker
mapper_resolution_worker.run(BATCH)
if STAGE=='resolve':print('PHASE1_STAGE_COMPLETED')
else:
 check_funds_with_bank_worker.run(ENVELOPE)
 block_funds_with_bank_worker.run(ENVELOPE)
 disburse_funds_from_bank_worker.run(BATCH)
 print('PHASE1_STAGE_COMPLETED')
'''
stage='resolve' if '--resolve' in sys.argv else 'dispatch'
if stage=='dispatch':
 with r.pg('bridge_db') as c:
  with c.cursor() as cur:
   cur.execute('SELECT sponsor_bank_dispatch_status FROM disbursement_batch_control WHERE id=%s',(batch,))
   if cur.fetchone()[0]=='PROCESSED':print('Existing native dispatch already processed; preserving idempotency.');sys.exit(0)
   cur.execute('SELECT (SELECT COUNT(*) FROM disbursements WHERE disbursement_batch_control_id=%s),(SELECT COUNT(DISTINCT disbursement_id) FROM disbursement_resolution_financial_address WHERE disbursement_batch_control_id=%s)',(batch,batch))
   expected,mapped=cur.fetchone()
   if expected!=mapped:raise RuntimeError('Every native instruction must have a financial address before dispatch.')
script='BATCH='+repr(batch)+'\nENVELOPE='+repr(envelope)+'\nSTAGE='+repr(stage)+'\n'+code
run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/bridge-celery-worker','--','python','-'],input=script,capture_output=True,text=True,timeout=120)
private=r.ROOT/'phase1-private-tests';private.mkdir(exist_ok=True,mode=0o700)
log=private/('native-bank-'+stage+'.log');log.write_text(run.stdout+run.stderr);log.chmod(0o600)
result={'stage':stage,'scope':'Local Example Bank and six existing fictional records only','worker_returned':run.returncode==0,'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
suffix='-household' if '--household' in sys.argv else ''
result['scope']='One enrolled fictional household; installed local Example Bank only' if suffix else result['scope']
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-bank-'+stage+suffix+'.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
sys.exit(run.returncode)
