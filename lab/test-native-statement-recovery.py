"""Inject one callback outage for a saved fictional statement, then retry natively."""
import json,sys,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT id FROM account_statements WHERE account_number='PHASE1-DEMO-TREASURY' AND account_statement_lob IS NOT NULL AND account_statement_generation_status='PENDING' ORDER BY id LIMIT 1");row=cur.fetchone()
  if not row:
   cur.execute("SELECT account_statement_lob FROM account_statements WHERE account_number='PHASE1-DEMO-TREASURY' AND account_statement_lob IS NOT NULL ORDER BY id DESC LIMIT 1");saved=cur.fetchone();assert saved
   # A new callback-only fixture copies an authentic saved fictional statement.
   # No financial ledger row, balance, payment or success status is created.
   cur.execute("INSERT INTO account_statements(account_number,account_statement_lob,account_statement_generation_status,account_statement_date,active,created_at,updated_at) VALUES('PHASE1-DEMO-TREASURY',%s,'PENDING',CURRENT_DATE,true,now(),now()) RETURNING id",(saved[0],));row=cur.fetchone()
  sid=row[0]
  cur.execute('SELECT COUNT(*),SUM(transaction_amount) FROM accounting_logs');before=cur.fetchone()
  cur.execute('SELECT account_number,book_balance FROM accounts ORDER BY account_number');balances=cur.fetchall()
script='''from unittest.mock import patch
from urllib.parse import urlparse
import importlib
m=importlib.import_module('openg2p_g2p_bridge_example_bank_celery.tasks.account_statement_generator')
assert urlparse(m._config.mt940_statement_callback_url).hostname=='bridge-api'
try:
    with patch.object(m.requests,'post',side_effect=m.requests.Timeout('Phase 1 fictional callback outage')):
        m.account_statement_generator.run(SID)
except m.requests.Timeout:
    print('PHASE1_OUTAGE_RECORDED')
else:
    raise AssertionError('Expected injected callback outage')
'''.replace('SID',str(sid))
def run(code,label):
 result=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/openg2p-g2p-bridge-example-bank-celery','--','python','-'],input=code,text=True,capture_output=True,timeout=60)
 p=r.ROOT/'phase1-private-tests'/('statement-'+label+'.log');p.write_text(result.stdout+result.stderr);p.chmod(0o600);assert result.returncode==0
run(script,'outage')
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:cur.execute('SELECT account_statement_generation_status FROM account_statements WHERE id=%s',(sid,));failure=cur.fetchone()[0]
assert failure=='FAILED'
run('from openg2p_g2p_bridge_example_bank_celery.tasks.account_statement_generator import account_statement_generator\naccount_statement_generator.run('+str(sid)+')\n','retry')
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute('SELECT account_statement_generation_status FROM account_statements WHERE id=%s',(sid,));success=cur.fetchone()[0]
  cur.execute('SELECT COUNT(*),SUM(transaction_amount) FROM accounting_logs');after=cur.fetchone()
  cur.execute('SELECT account_number,book_balance FROM accounts ORDER BY account_number');after_balances=cur.fetchall()
report={'scope':'Existing saved local-bank fictional statement callback failure and retry; no new payment','recorded_failure_status':failure,'native_retry_status':success,'no_ledger_or_balance_changes':before==after and balances==after_balances,'status':'passed' if success=='SUCCESS' and before==after and balances==after_balances else 'failed'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-statement-recovery.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['status']=='passed'
