import subprocess,json,yaml,pathlib
def patch_env(name,env):
 subprocess.run(['kubectl','set','env','-n','nigeria','deploy/'+name,*[k+'='+v for k,v in env.items()]],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
# Point the published portal at its matching PBMS 1.3 database.
obj=json.loads(subprocess.check_output(['kubectl','get','deploy','pbms-beneficiary-portal','-n','nigeria','-o','json']))
spec=obj['spec']['template']['spec']
for c in spec['containers']:
 for e in c.get('env',[]):
  if e['name']=='PORTAL_DB_HOSTNAME':e['value']='portal-backend-postgresql'
  if e['name']=='PORTAL_DB_DBNAME':e['value']='portalpbmsdb'
  if e['name']=='PORTAL_DB_USERNAME':e['value']='portaluser'
  if e['name']=='PORTAL_DB_PASSWORD':e['valueFrom']={'secretKeyRef':{'name':'portal-backend-postgresql','key':'password'}}
subprocess.run(['kubectl','patch','deploy','pbms-beneficiary-portal','-n','nigeria','--type','merge','-p',json.dumps({'spec':{'template':{'spec':spec}}})],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
issuer='https://keycloak.openg2p.localhost/realms/beneficiary'
patch_env('pbms-beneficiary-portal',{'PORTAL_AUTH_COOKIE_PREFIX':'NG-BENE-','PORTAL_AUTH_DEFAULT_ISSUERS':json.dumps([issuer,'https://esignet.openg2p.localhost']),'PORTAL_AUTH_DEFAULT_JWKS_URLS':json.dumps([issuer+'/protocol/openid-connect/certs','https://esignet.openg2p.localhost/.well-known/jwks.json'])})
# Add a staff-facing administrator UI for the separate portal demonstration workspace.
vs={'apiVersion':'networking.istio.io/v1','kind':'VirtualService','metadata':{'name':'portal-backend-odoo','namespace':'nigeria'},'spec':{'hosts':['portal-admin.openg2p.localhost'],'gateways':['internal'],'http':[{'route':[{'destination':{'host':'portal-backend-odoo','port':{'number':80}}}]}]}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(vs),text=True,check=True)
print('Beneficiary portal connected to its matching programme backend.')
