"""Regenerate one local statement from its authentic synthetic ledger records."""
import json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT id FROM account_statements WHERE account_number='PHASE1-DEMO-TREASURY' ORDER BY id LIMIT 1");sid=cur.fetchone()[0]
  cur.execute("UPDATE accounting_logs SET reported_in_mt940=false WHERE account_number='PHASE1-DEMO-TREASURY'")
script='''from openg2p_g2p_bridge_example_bank_celery.tasks.account_statement_generator import account_statement_generator
account_statement_generator.run(STATEMENT_ID)
print('PHASE1_STATEMENT_REGENERATED')
'''.replace('STATEMENT_ID',str(sid))
result=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/openg2p-g2p-bridge-example-bank-celery','--','python','-'],input=script,text=True,capture_output=True,timeout=60)
p=r.ROOT/'phase1-private-tests/regenerated-statement.log';p.write_text(result.stdout+result.stderr);p.chmod(0o600)
print(json.dumps({'worker_returned':result.returncode==0,'scope':'Regenerated existing local synthetic statement; no new payment issued'}))
sys.exit(result.returncode)
