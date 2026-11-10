"""Pin two inspected native fixes, with private backups and rollout checks."""
import datetime as dt,hashlib,json,subprocess,sys
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
def deploy_file(name,path,cmname,transform):
 original=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+name,'--','cat',path],text=True,stderr=subprocess.DEVNULL)
 patched=transform(original);compile(patched,path,'exec')
 if patched==original:
  print(cmname,'already installed; no deployment change.');return
 (backup/(cmname+'.py')).write_text(original)
 deployment=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']))
 saved=backup/(name+'.json');saved.write_text(json.dumps(deployment));saved.chmod(0o600)
 cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':cmname,'namespace':'nigeria'},'data':{path.rsplit('/',1)[-1]:patched}}
 subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
 spec=deployment['spec']['template']['spec'];container=spec['containers'][0]
 spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!=cmname]+[{'name':cmname,'configMap':{'name':cmname}}]
 container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['mountPath']!=path]+[{'name':cmname,'mountPath':path,'subPath':path.rsplit('/',1)[-1],'readOnly':True}]
 deployment['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})[cmname]=hashlib.sha256(patched.encode()).hexdigest()
 run=subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':deployment['spec']['template']}})],capture_output=True,text=True);run.check_returncode()
 subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/'+name,'--timeout=90s'],check=True)
def counter(source):
 if 'phase1 durable entitlement count' in source:return source
 marker='            beneficiary_list.entitlement_number_of_attempts += 1'
 assert marker in source
 source=source.replace('from openg2p_bg_task_registry_adapters.factory','from openg2p_bg_task_models.models import BeneficiaryListDetails\nfrom openg2p_bg_task_registry_adapters.factory',1)
 code='''            # phase1 durable entitlement count
            details = bg_task_session.query(BeneficiaryListDetails).filter(
                BeneficiaryListDetails.beneficiary_list_id == beneficiary_list.beneficiary_list_id
            ).all()
            beneficiary_list.number_of_entitlements_processed = sum(
                any(float(value) > 0 for value in detail.get("entitlement", {}).values())
                for chunk in details for detail in chunk.registrant_details
            )
'''
 return source.replace(marker,code+marker,1)
def replay(source):
 if 'phase1 processed statement guard' in source:return source
 marker='        if not account_statement:\n            return'
 assert marker in source
 return source.replace(marker,marker+'\n\n        # phase1 processed statement guard\n        if account_statement.statement_process_status == ProcessStatus.PROCESSED.value:\n            return',1)
def bank_replay(source):
 if 'phase1 completed bank batch guard' in source:return source
 marker='                    InitiatePaymentBatchRequest.batch_id == payment_request_batch_id\n                )'
 assert marker in source
 source=source.replace(marker,marker+'.with_for_update()',1)
 marker='        try:\n            initiate_payment_requests = ('
 assert marker in source
 guard='''        # phase1 completed bank batch guard
        if not initiate_payment_batch_request or initiate_payment_batch_request.payment_status == PaymentStatus.SUCCESS:
            return
'''
 return source.replace(marker,guard+marker,1)
def statement_retry(source):
 if 'phase1 durable statement retry' in source:return source
 source=source.replace('    AccountStatement,','    AccountStatement,\n    AccountStatementStatus,',1)
 marker='@celery_app.task(name="account_statement_generator")'
 helper='''# phase1 durable statement retry
def upload_saved_statement(statement, session):
    try:
        response = requests.post(
            _config.mt940_statement_callback_url,
            files={"statement_file": ("statement.mt940", statement.account_statement_lob, "text/plain")},
            timeout=15,
        )
        response.raise_for_status()
        if response.json().get("response_header", {}).get("response_status") != "SUCCESS":
            raise ValueError("Bridge rejected the saved statement")
        statement.account_statement_generation_status = AccountStatementStatus.SUCCESS
        session.commit()
    except (requests.RequestException, ValueError):
        statement.account_statement_generation_status = AccountStatementStatus.FAILED
        session.commit()
        raise


'''
 source=source.replace(marker,helper+marker,1)
 marker='        account = (\n'
 guard='''        if account_statement.account_statement_generation_status == AccountStatementStatus.SUCCESS:
            return
        if account_statement.account_statement_lob:
            upload_saved_statement(account_statement, session)
            return

'''
 source=source.replace(marker,guard+marker,1)
 marker='            _logger.error("Account logs not found")\n            return'
 source=source.replace(marker,'            account_statement.account_statement_generation_status = AccountStatementStatus.NOT_APPLICABLE\n            session.commit()\n'+marker,1)
 start=source.index('        # Prepare the in-memory file')
 return source[:start]+'        upload_saved_statement(account_statement, session)\n'
def statement_date(source):
 marker='default=datetime.date(datetime.utcnow())'
 if marker not in source:
  assert 'default=lambda: datetime.utcnow().date()' in source;return source
 return source.replace(marker,'default=lambda: datetime.utcnow().date()',1)
def positive_amounts(source):
 if 'allow_inf_nan=False' in source:return source
 source=source.replace('from pydantic import BaseModel','from pydantic import BaseModel, Field',1)
 for field in ['total_funds_needed','amount','payment_amount']:
  source=source.replace('    '+field+': float\n','    '+field+': float = Field(gt=0, allow_inf_nan=False)\n')
 return source
def statement_lock(source):
 if 'phase1 statement concurrency lock' in source:return source
 source=source.replace('import logging','from contextlib import contextmanager\nfrom sqlalchemy import text\nimport logging',1)
 marker='@celery_app.task(name="mt940_processor_worker")'
 helper='''# phase1 statement concurrency lock
@contextmanager
def statement_processing_lock(statement_id):
    with _engine.get("db_engine_bridge").connect() as connection:
        key = {"key": "phase1-mt940:" + statement_id}
        acquired = connection.execute(text("SELECT pg_try_advisory_lock(hashtextextended(:key, 0))"), key).scalar()
        try:
            yield acquired
        finally:
            if acquired:
                connection.execute(text("SELECT pg_advisory_unlock(hashtextextended(:key, 0))"), key)


'''
 source=source.replace(marker,helper+marker,1)
 start=source.index('def mt940_processor_worker(statement_id: str):')
 body_start=source.index('\n',start)+1;end=source.index('\n\ndef process_reversal_of_debits',body_start)
 body=source[body_start:end]
 wrapped='    with statement_processing_lock(statement_id) as acquired:\n        if not acquired:\n            return\n'+''.join('    '+line if line.strip() else line for line in body.splitlines(keepends=True))
 return source[:body_start]+wrapped+source[end:]
deploy_file('pbms-celery-worker','/usr/local/lib/python3.12/site-packages/openg2p_bg_task_celery_workers/tasks/entitlement_summary_worker.py','phase1-entitlement-counter',counter)
deploy_file('bridge-celery-worker','/usr/local/lib/python3.12/site-packages/openg2p_g2p_bridge_celery_workers/tasks/mt940_processor.py','phase1-statement-replay-guard',replay)
deploy_file('openg2p-g2p-bridge-example-bank-celery','/opt/bitnami/python/lib/python3.12/site-packages/openg2p_g2p_bridge_example_bank_celery/tasks/process_payment.py','phase1-bank-payment-replay-guard',bank_replay)
deploy_file('openg2p-g2p-bridge-example-bank-celery','/opt/bitnami/python/lib/python3.12/site-packages/openg2p_g2p_bridge_example_bank_celery/tasks/account_statement_generator.py','phase1-bank-statements',statement_retry)
for name in ['openg2p-g2p-bridge-example-bank-api','openg2p-g2p-bridge-example-bank-celery']:
 package='openg2p_example_bank_models' if name.endswith('-api') else 'openg2p_g2p_bridge_example_bank_models'
 deploy_file(name,'/opt/bitnami/python/lib/python3.12/site-packages/'+package+'/models/account_statement.py','phase1-bank-statement-date',statement_date)
for file in ['account.py','payment_request.py']:
 deploy_file('openg2p-g2p-bridge-example-bank-api','/opt/bitnami/python/lib/python3.12/site-packages/openg2p_example_bank_models/schemas/'+file,'phase1-bank-positive-'+file.replace('.py','').replace('_','-'),positive_amounts)
deploy_file('bridge-celery-worker','/usr/local/lib/python3.12/site-packages/openg2p_g2p_bridge_celery_workers/tasks/mt940_processor.py','phase1-statement-replay-guard',statement_lock)
print('Native durable entitlement counter and processed-statement replay guard installed with private rollback snapshots.')
