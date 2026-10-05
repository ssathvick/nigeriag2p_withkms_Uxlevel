import pathlib,json,subprocess,base64,sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
path=pathlib.Path('/opt/openg2p-lab/package-audit/openg2p_registry_core/services/g2p_register_metadata_service.py')
code=path.read_text().replace('async_sessionmaker(dbengine.get(), expire_on_commit=False)','get_async_session_maker()')
cm=json.loads(subprocess.check_output(['kubectl','get','cm','registry-package-repair','-n','nigeria','-o','json']))
cm['data']['g2p_register_metadata_service.py']=code;cm['metadata'].pop('resourceVersion',None);cm['metadata'].pop('managedFields',None)
for filename in ['g2p_registrant_authentication_service.py','g2p_ingest_service.py']:
 source=path.parent/filename
 cm['data'][filename]='from openg2p_fastapi_common.context import get_async_session_maker\n'+source.read_text()
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
for name in ['register-staff-portal-api','register-partner-api','register-celery-worker']:
 obj=json.loads(subprocess.check_output(['kubectl','get','deploy',name,'-n','nigeria','-o','json']))
 spec=obj['spec']['template']['spec']
 for c in spec['containers']:
  for filename in ['g2p_register_metadata_service.py','g2p_registrant_authentication_service.py','g2p_ingest_service.py']:
   target='/usr/local/lib/python3.12/site-packages/openg2p_registry_core/services/'+filename
   mounts=c.setdefault('volumeMounts',[])
   if not any(m['mountPath']==target for m in mounts):
    mounts.append({'name':'registry-package-repair','mountPath':target,'subPath':filename,'readOnly':True})
 subprocess.run(['kubectl','patch','deploy',name,'-n','nigeria','--type','merge','-p',json.dumps({'spec':{'template':{'spec':spec}}})],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
secret=json.loads(subprocess.check_output(['kubectl','get','secret','register-awe-callback-hmac','-n','nigeria','-o','json']))
hmac=base64.b64decode(secret['data']['hmac-secret']).decode()
q=lambda s:"'"+s.replace("'","''")+"'"
query('awe',f"INSERT INTO callback_secret(id,caller_service,secret_hash,status,created_at,updated_at) VALUES('register','http://register-staff-portal-api/awe/webhooks/decision',{q(hmac)},'active',now(),now()) ON CONFLICT(id) DO UPDATE SET secret_hash=EXCLUDED.secret_hash,caller_service=EXCLUDED.caller_service,updated_at=now();")
for field in ['core_translation','domain_translation']:
 query('register',f"UPDATE registry_languages SET {field}=replace({field}::text,'Fayda ID','Lab Identity ID')::json WHERE {field}::text LIKE '%Fayda ID%';")
print('Registry tab-session bug, local identity label and AWE callback registration repaired.')
