import copy,json,pathlib,subprocess,requests,yaml
base=['kubectl','-n','nigeria']
def read(kind,name): return json.loads(subprocess.check_output(base+['get',kind,name,'-o','json']))
def apply(obj): subprocess.run(base+['apply','-f','-'],input=json.dumps(obj),text=True,check=True)
host='beneficiary-consent.nigeriag2p.com'
ip=subprocess.check_output(base+['get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
kc='http://'+ip
pw=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':pw},timeout=15); r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
url=kc+'/admin/realms/beneficiary/clients'
client_id='nigeria-consent-beneficiary-ui'
r=s.get(url,params={'clientId':client_id},timeout=15);r.raise_for_status()
clients=r.json()
if not clients:
 r=s.post(url,json={'clientId':client_id,'enabled':True,'publicClient':True,'standardFlowEnabled':True,'directAccessGrantsEnabled':False,'redirectUris':['https://'+host+'/*'],'webOrigins':['https://'+host],'attributes':{'pkce.code.challenge.method':'S256'}},timeout=15);r.raise_for_status()
else:
 c=clients[0]
 if not c.get('publicClient') or c.get('redirectUris')!=['https://'+host+'/*']: raise SystemExit('Existing client differs; refusing to overwrite')
cfg={'apiBaseUrl':'','keycloak':{'url':'https://keycloak.nigeriag2p.com','realm':'beneficiary','clientId':client_id},'adminRole':'CONSENT_MANAGER_ADMIN','approverRole':'CONSENT_MANAGER_APPROVER'}
apply({'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nigeria-consent-beneficiary-ui-config','namespace':'nigeria'},'data':{'config.json':json.dumps(cfg)}})
source=read('deployment','commons-services-cm-ui');pod=copy.deepcopy(source['spec']['template']);labels={'app':'nigeria-consent-beneficiary-ui'};pod['metadata']={'labels':labels}
for v in pod['spec']['volumes']:
 if v['name']=='runtime-config': v['configMap']['name']='nigeria-consent-beneficiary-ui-config'
apply({'apiVersion':'apps/v1','kind':'Deployment','metadata':{'name':'nigeria-consent-beneficiary-ui','namespace':'nigeria'},'spec':{'replicas':1,'selector':{'matchLabels':labels},'template':pod}})
apply({'apiVersion':'v1','kind':'Service','metadata':{'name':'nigeria-consent-beneficiary-ui','namespace':'nigeria'},'spec':{'selector':labels,'ports':[{'name':'http','port':80,'targetPort':8080}]}})
apply({'apiVersion':'networking.istio.io/v1','kind':'VirtualService','metadata':{'name':'nigeria-consent-beneficiary','namespace':'nigeria'},'spec':{'gateways':['internal'],'hosts':[host],'http':[{'name':'beneficiary-api','match':[{'uri':{'prefix':'/consent/'}}],'route':[{'destination':{'host':'nigeria-consent-beneficiary-api','port':{'number':80}}}]},{'name':'beneficiary-ui','match':[{'uri':{'prefix':'/'}}],'route':[{'destination':{'host':'nigeria-consent-beneficiary-ui','port':{'number':80}}}]}]}})
subprocess.run(base+['rollout','status','deployment/nigeria-consent-beneficiary-ui','--timeout=120s'],check=True)
