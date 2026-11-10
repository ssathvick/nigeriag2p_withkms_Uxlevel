"""Verify saved native results and replay a completed statement without new payments."""
import datetime as dt,json,subprocess,sys
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
out=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence')
run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/pbms-celery-worker','--','python','-'],input='from openg2p_bg_task_celery_workers.tasks.entitlement_summary_worker import entitlement_summary_worker\nentitlement_summary_worker.run(8)\n',text=True,capture_output=True,timeout=60)
p=r.ROOT/'phase1-private-tests/household-summary.log';p.write_text(run.stdout+run.stderr);p.chmod(0o600)
def snapshot():
 with r.pg('bridge_db') as c:
  with c.cursor() as cur:
   cur.execute('SELECT COUNT(*),COUNT(DISTINCT disbursement_id) FROM disbursement_recons');recons=cur.fetchone()
   cur.execute('SELECT COUNT(*) FROM disbursement_error_recons');errors=cur.fetchone()[0]
   cur.execute('SELECT disbursement_envelope_id,number_of_disbursements_reconciled FROM envelope_batch_status_for_cash ORDER BY disbursement_envelope_id');counts=cur.fetchall()
   cur.execute('SELECT COUNT(*) FROM account_statements');receipts=cur.fetchone()[0]
 return {'reconciliation_rows':recons[0],'distinct_instructions':recons[1],'exceptions':errors,'receipts':receipts,'envelope_counters':counts}
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute("SELECT s.statement_id,l.statement_lob FROM account_statements s JOIN account_statement_lobs l USING(statement_id) WHERE s.statement_process_status='PROCESSED' ORDER BY s.created_at DESC LIMIT 1");sid,lob=cur.fetchone()
  cur.execute("SELECT d.id,d.disbursement_quantity,b.fa_resolution_status,b.sponsor_bank_dispatch_status FROM disbursements d JOIN disbursement_batch_control b ON b.id=d.disbursement_batch_control_id WHERE d.beneficiary_id='IQS-REG-HH-9300745d55295cdb' AND d.disbursement_cycle_id=4");household=cur.fetchall()
assert len(household)==1 and household[0][1]==25000
before=snapshot()
resp=requests.post(r.svc('bridge-api')+'/upload_mt940',files={'statement_file':('phase1-replay.mt940',lob.encode(),'text/plain')},timeout=15);resp.raise_for_status()
returned=resp.json()['response_body']['response_payload']['statement_id'];assert returned==sid
script='from openg2p_g2p_bridge_celery_workers.app import Initializer\nInitializer()\nfrom openg2p_g2p_bridge_celery_workers.tasks.mt940_processor import mt940_processor_worker\nmt940_processor_worker.run('+repr(sid)+')\n'
run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/bridge-celery-worker','--','python','-'],input=script,text=True,capture_output=True,timeout=60)
p=r.ROOT/'phase1-private-tests/statement-replay.log';p.write_text(run.stdout+run.stderr);p.chmod(0o600)
after=snapshot();assert before==after and run.returncode==0
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT book_balance FROM accounts WHERE account_number='LAB-HH-000001'");balance=float(cur.fetchone()[0])
pb=r.Odoo('pbms-odoo','pbmsdb');counter=pb.call('g2p.beneficiary.list','read',[[8]],{'fields':['number_of_entitlements_processed']})[0]['number_of_entitlements_processed']
report={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Previously enrolled fictional household through native PBMS SPAR Bridge local Example Bank and reconciliation','entitlement_ngn':25000,'native_entitlement_count':counter,'local_account_balance_ngn':balance,'mapping_status':household[0][2],'dispatch_status':household[0][3],'all_reconciled_instructions':after['distinct_instructions'],'reconciliation_exceptions':after['exceptions'],'statement_replay_preserved_counts':before==after,'automatic_household_settlement_and_reconciliation':True,'status':'passed' if balance==25000 and counter==1 and after['distinct_instructions']==9 and after['exceptions']==0 else 'failed','limitations':['Nine instructions only; not 1M batch acceptance','All local synthetic data and balances; no live government or payment rails','Independent failure recovery and client acceptance remain pending']}
(out/'native-household-payment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
