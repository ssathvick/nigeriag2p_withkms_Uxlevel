import subprocess,json
name='bridge-celery-worker'
path='/usr/local/lib/python3.12/site-packages/openg2p_g2p_bridge_mapper_connectors/app.py'
code=subprocess.check_output(['kubectl','exec','-n','nigeria','deploy/'+name,'--','cat',path],text=True)
code=code.replace('        KeymanagerCryptoHelper(name="spar_mapper_crypto")','')
code=code.replace('        KeymanagerCryptoHelper()','        KeymanagerCryptoHelper()\n        KeymanagerCryptoHelper(name="spar_mapper_crypto", api_base_url="http://commons-services-keymanager/v1/keymanager", auth_enabled=False, sign_app_id="OPENG2P_BRIDGE", sign_ref_id="")')
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'bridge-mapper-repair','namespace':'nigeria'},'data':{'app.py':code}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True,stdout=subprocess.DEVNULL)
obj=json.loads(subprocess.check_output(['kubectl','get','deploy',name,'-n','nigeria','-o','json']))
spec=obj['spec']['template']['spec']
if not any(v['name']=='bridge-mapper-repair' for v in spec.setdefault('volumes',[])):spec['volumes'].append({'name':'bridge-mapper-repair','configMap':{'name':'bridge-mapper-repair'}})
for c in spec['containers']:
 if not any(m['mountPath']==path for m in c.setdefault('volumeMounts',[])):c['volumeMounts'].append({'name':'bridge-mapper-repair','mountPath':path,'subPath':'app.py','readOnly':True})
subprocess.run(['kubectl','patch','deploy',name,'-n','nigeria','--type','merge','-p',json.dumps({'spec':{'template':{'spec':spec}}})],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
env={'G2P_BRIDGE_MAPPER_CONNECTORS_SPAR_MAPPER_URL':'http://spar-openg2p-spar-mapper-api/mapper/resolve','G2P_BRIDGE_MAPPER_CONNECTORS_SPAR_MAPPER_API_SIGN_ENABLED':'true','G2P_BRIDGE_CELERY_WORKERS_KEYMANAGER_SIGN_APP_ID':'OPENG2P_BRIDGE','G2P_BRIDGE_CELERY_WORKERS_KEYMANAGER_SIGN_REF_ID':'','G2PCONNECT_MAPPER_CLIENT_API_BASE_URL':'http://spar-openg2p-spar-mapper-api/mapper'}
subprocess.run(['kubectl','set','env','-n','nigeria','deploy/'+name,*[k+'='+v for k,v in env.items()]],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('Bridge worker configured to use signed SPAR mapper calls.')
