"""Retry only the retained fictional treasury statement backlog through native code."""
import json,sys,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT id FROM account_statements WHERE account_number='PHASE1-DEMO-TREASURY' AND account_statement_generation_status IN ('PENDING','FAILED') ORDER BY id");ids=[x[0] for x in cur.fetchall()]
code='from openg2p_g2p_bridge_example_bank_celery.tasks.account_statement_generator import account_statement_generator\nfor sid in '+repr(ids)+':\n account_statement_generator.run(sid)\n'
run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/openg2p-g2p-bridge-example-bank-celery','--','python','-'],input=code,text=True,capture_output=True,timeout=120)
p=r.ROOT/'phase1-private-tests/statement-backlog.log';p.write_text(run.stdout+run.stderr);p.chmod(0o600);assert run.returncode==0
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT account_statement_generation_status,COUNT(*) FROM account_statements WHERE account_number='PHASE1-DEMO-TREASURY' GROUP BY account_statement_generation_status");states=dict(cur.fetchall())
report={'scope':'Native retries for retained fictional treasury statement backlog only','states':states,'status':'passed' if not states.get('PENDING') and not states.get('FAILED') else 'failed','note':'Empty ledger requests are NOT_APPLICABLE, not successful statement tests.'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-statement-backlog.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['status']=='passed'
