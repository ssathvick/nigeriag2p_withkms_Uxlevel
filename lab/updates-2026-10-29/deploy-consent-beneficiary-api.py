"""Deploy an isolated consent beneficiary API; do not expose it publicly."""
import copy, json, subprocess

base=['kubectl','-n','nigeria']
def read(kind,name):
    return json.loads(subprocess.check_output(base+['get',kind,name,'-o','json']))
def apply(obj):
    subprocess.run(base+['apply','-f','-'],input=json.dumps(obj),text=True,check=True)
source=read('deployment','commons-services-cm-api')
pod=copy.deepcopy(source['spec']['template'])
labels={'app':'nigeria-consent-beneficiary-api'}
pod['metadata']={'labels':labels}
container=pod['spec']['containers'][0]
for item in container.get('env',[]):
    if item['name']=='CONSENT_MANAGER_API_AUDIENCE': item['value']='beneficiary'
    if item['name']=='CONSENT_MANAGER_AUTH_ISSUER': item['value']='https://keycloak.nigeriag2p.com/realms/beneficiary'
    if item['name']=='CONSENT_MANAGER_AUTH_JWKS_URL': item['value']='http://commons-keycloak/realms/beneficiary/protocol/openid-connect/certs'
deploy={'apiVersion':'apps/v1','kind':'Deployment','metadata':{'name':'nigeria-consent-beneficiary-api','namespace':'nigeria'},'spec':{'replicas':1,'selector':{'matchLabels':labels},'template':pod}}
service={'apiVersion':'v1','kind':'Service','metadata':{'name':'nigeria-consent-beneficiary-api','namespace':'nigeria'},'spec':{'selector':labels,'ports':[{'name':'http','port':80,'targetPort':8000}]}}
apply(deploy); apply(service)
subprocess.run(base+['rollout','status','deployment/nigeria-consent-beneficiary-api','--timeout=120s'],check=True)
