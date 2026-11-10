import json,re,subprocess,sys
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute('SELECT id,account_statement_generation_status,account_statement_lob IS NOT NULL FROM account_statements ORDER BY id');print('Bank statement states',cur.fetchall())
  cur.execute('SELECT account_number,COUNT(*),COUNT(*) FILTER(WHERE reported_in_mt940=false) FROM accounting_logs GROUP BY account_number');print('Synthetic ledger statement coverage',cur.fetchall())
log=subprocess.check_output(['kubectl','-n','nigeria','logs','deploy/openg2p-g2p-bridge-example-bank-celery','--tail=150'],text=True,stderr=subprocess.DEVNULL)
p=r.ROOT/'phase1-private-tests/statement-worker.log';p.write_text(log);p.chmod(0o600)
for msg in re.findall(r'[a-zA-Z_.]+(?:Error|Exception):[^\n]+',log.replace('\\n','\n'))[-4:]:print(msg[:250])
for msg in re.findall(r'[^\n]*(?:Account logs not found|Failed to upload MT940|unregistered task)[^\n]*',log.replace('\\n','\n'))[-4:]:print(msg[:250])
