"""Make duplicate native MT940 submissions reuse a stable receipt."""
import datetime as dt,hashlib,json,subprocess,sys
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
name='bridge-api';path='/usr/local/lib/python3.12/site-packages/openg2p_g2p_bridge_partner_api/services/account_statement.py'
original=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+name,'--','cat',path],text=True)
if 'statement_id = str(uuid.uuid4())' not in original:raise RuntimeError('Unexpected native statement service; inspect before patching.')
patched=original.replace('import uuid','import uuid\nimport hashlib\nfrom sqlalchemy import select\nfrom sqlalchemy.exc import IntegrityError')
patched=patched.replace('statement_id = str(uuid.uuid4())','statement_id = str(uuid.uuid5(uuid.NAMESPACE_URL, hashlib.sha256(statement_file).hexdigest()))')
patched=patched.replace('        async with session_maker() as session:\n            statement = AccountStatement(',"        async with session_maker() as session:\n            existing = await session.execute(select(AccountStatement).where(AccountStatement.statement_id == statement_id))\n            if existing.scalars().first():\n                return statement_id\n            statement = AccountStatement(")
patched=patched.replace('            await session.commit()',"            try:\n                await session.commit()\n            except IntegrityError:\n                await session.rollback()\n                existing = await session.execute(select(AccountStatement).where(AccountStatement.statement_id == statement_id))\n                if not existing.scalars().first():\n                    raise")
compile(patched,path,'exec')
backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700);(backup/'statement-service.py').write_text(original)
deploy=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']));(backup/'deployment.json').write_text(json.dumps(deploy));(backup/'deployment.json').chmod(0o600)
with r.pg('bridge_db') as c:
 with c.cursor() as cur:cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS phase1_statement_idempotency ON account_statements(statement_id)')
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'phase1-native-statement-idempotency','namespace':'nigeria'},'data':{'account_statement.py':patched}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
s=deploy['spec']['template']['spec'];container=s['containers'][0];mount='phase1-native-statement-idempotency'
s['volumes']=[v for v in s.get('volumes',[]) if v['name']!=mount]+[{'name':mount,'configMap':{'name':mount}}]
container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['mountPath']!=path]+[{'name':mount,'mountPath':path,'subPath':'account_statement.py','readOnly':True}]
deploy['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['iqs-phase1-statement-idempotency']=hashlib.sha256(patched.encode()).hexdigest()
result=subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':deploy['spec']['template']}})],capture_output=True,text=True);result.check_returncode()
subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/'+name,'--timeout=90s'],check=True)
print('Native statement upload now uses content-derived receipts and a uniqueness constraint; duplicate receipts are idempotent.')
