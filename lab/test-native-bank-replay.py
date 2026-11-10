"""Repeat a completed simulator worker; verify no debit credit ledger or batch changes."""
import json,sys,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
def snapshot():
 with r.pg('example_bank_db','example-bank-postgresql') as c:
  with c.cursor() as cur:
   cur.execute('SELECT account_number,book_balance,available_balance,blocked_amount FROM accounts ORDER BY account_number');balances=cur.fetchall()
   cur.execute('SELECT COUNT(*),SUM(transaction_amount) FROM accounting_logs');ledger=cur.fetchone()
   cur.execute('SELECT batch_id,payment_status,payment_initiate_attempts FROM initiate_payment_batch_requests ORDER BY batch_id');batches=cur.fetchall()
 return {'balances':balances,'ledger':ledger,'batches':batches}
before=snapshot();batch=next(x[0] for x in before['batches'] if x[1]=='SUCCESS')
script='from openg2p_g2p_bridge_example_bank_celery.tasks.process_payment import process_payments_worker\nprocess_payments_worker.run('+repr(batch)+')\n'
run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/openg2p-g2p-bridge-example-bank-celery','--','python','-'],input=script,text=True,capture_output=True,timeout=60)
p=r.ROOT/'phase1-private-tests/bank-replay.log';p.write_text(run.stdout+run.stderr);p.chmod(0o600)
after=snapshot();result={'scope':'Completed native local-bank batch replay against actual fictional ledger','status':'passed' if run.returncode==0 and before==after else 'failed','no_balance_ledger_or_batch_changes':before==after}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-bank-replay.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert result['status']=='passed'
