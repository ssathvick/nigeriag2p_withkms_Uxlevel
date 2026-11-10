"""Correct simulator statement balances and deliver only to the local Bridge."""
import datetime as dt,json,hashlib,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
name='openg2p-g2p-bridge-example-bank-celery'
path='/opt/bitnami/python/lib/python3.12/site-packages/openg2p_g2p_bridge_example_bank_celery/tasks/account_statement_generator.py'
code=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+name,'--','cat',path],text=True)
old='        mt940_opening_balance = mt940_writer.create_balance(\n            Decimal("100000000"), statement_date, currency\n        )'
new='        opening_amount = Decimal(str(account.book_balance)) + sum(\n            (Decimal(str(item.transaction_amount)) if item.debit_credit == DebitCreditTypes.DEBIT else -Decimal(str(item.transaction_amount)))\n            for item in account_logs\n        )\n        mt940_opening_balance = mt940_writer.create_balance(opening_amount, statement_date, currency)'
if old not in code:raise RuntimeError('Unexpected statement generator; inspect before patching.')
patched=code.replace(old,new)
backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
(backup/'account_statement_generator.py').write_text(code)
d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']))
(backup/'deployment.json').write_text(json.dumps(d));(backup/'deployment.json').chmod(0o600)
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'phase1-bank-statements','namespace':'nigeria'},'data':{'account_statement_generator.py':patched}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
s=d['spec']['template']['spec'];container=s['containers'][0]
s['volumes']=[x for x in s.get('volumes',[]) if x['name']!='phase1-bank-statements']+[{'name':'phase1-bank-statements','configMap':{'name':'phase1-bank-statements'}}]
container['volumeMounts']=[x for x in container.get('volumeMounts',[]) if x['mountPath']!=path]+[{'name':'phase1-bank-statements','mountPath':path,'subPath':'account_statement_generator.py','readOnly':True}]
envkey='EXAMPLE_BANK_CELERY_MT940_STATEMENT_CALLBACK_URL'
container['env']=[x for x in container.get('env',[]) if x['name']!=envkey]+[{'name':envkey,'value':'http://bridge-api/upload_mt940'}]
d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['iqs-phase1-statements']=hashlib.sha256(patched.encode()).hexdigest()
result=subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':d['spec']['template']}})],capture_output=True,text=True);result.check_returncode()
subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/'+name,'--timeout=90s'],check=True)
print('Simulator statement opening balance derives from ledger. Callback restricted to local Bridge; private backup retained.')
