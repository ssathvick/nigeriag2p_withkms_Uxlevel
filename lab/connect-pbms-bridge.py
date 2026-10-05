import subprocess,json,datetime,requests,base64
ip=lambda s:subprocess.check_output(['kubectl','get','svc',s,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
km='http://'+ip('commons-services-keymanager')+'/v1/keymanager';now=datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
r=requests.post(km+'/generateMasterKey/CERTIFICATE',json={'id':'nigeria-lab','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_PBMS','referenceId':'','force':False}});r.raise_for_status();cert=r.json()['response']['certificate']
r=requests.post(km+'/uploadOtherDomainCertificate',json={'id':'nigeria-lab','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'PARTNER_OPENG2P_PBMS','certificateData':cert}});r.raise_for_status();print('Register PBMS signing certificate',r.json())
name='bridge-api';path='/usr/local/lib/python3.12/site-packages/openg2p_g2p_bridge_partner_api/app.py'
code=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+name,'--','cat',path],text=True)
code=code.replace('        KeymanagerCryptoHelper()','        KeymanagerCryptoHelper(api_base_url="http://commons-services-keymanager/v1/keymanager", auth_enabled=False, sign_app_id="OPENG2P_BRIDGE")')
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'bridge-api-repair','namespace':'nigeria'},'data':{'app.py':code}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True)
d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']));s=d['spec']['template']['spec'];c=s['containers'][0]
s['volumes']=[v for v in s.get('volumes',[]) if v['name']!='bridge-api-repair']+[{'name':'bridge-api-repair','configMap':{'name':'bridge-api-repair'}}]
c['volumeMounts']=[v for v in c.get('volumeMounts',[]) if v['name']!='bridge-api-repair']+[{'name':'bridge-api-repair','mountPath':path,'subPath':'app.py','readOnly':True}]
subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':d['spec']['template']}})],check=True,stderr=subprocess.DEVNULL)
subprocess.run(['kubectl','-n','nigeria','set','env','deploy/pbms-celery-worker','BG_TASK_CELERY_WORKERS_G2P_BRIDGE_BASE_URL=http://bridge-api','BG_TASK_CELERY_WORKERS_SIGN_KEY_KEYMANAGER_REF_ID='],check=True,stderr=subprocess.DEVNULL)
