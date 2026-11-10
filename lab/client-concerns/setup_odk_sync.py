import json,secrets,subprocess,requests
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
root=Path(__file__).parent
exec((root/'inspect_demo_roles.py').read_text().split('user=s.get')[0])
dest=Path('/opt/openg2p-lab/odk-sync');dest.mkdir(mode=0o700,exist_ok=True)
cfgpath=dest/'config.json';cfg=json.loads(cfgpath.read_text()) if cfgpath.exists() else {}
def persist():cfgpath.write_text(json.dumps(cfg));cfgpath.chmod(0o600)
cid='nsipa-odk-registry-sync'
found=s.get(base+'/clients',params={'clientId':cid}).json()
if not found:
 res=s.post(base+'/clients',json={'clientId':cid,'enabled':True,'publicClient':False,'serviceAccountsEnabled':True,'standardFlowEnabled':False,'directAccessGrantsEnabled':False,'fullScopeAllowed':True});res.raise_for_status()
 found=s.get(base+'/clients',params={'clientId':cid}).json()
client=found[0]['id'];cfg['client_id']=cid;cfg['client_secret']=s.get(base+'/clients/'+client+'/client-secret').json()['value'];persist()
account=s.get(base+'/clients/'+client+'/service-account-user').json()
target=s.get(base+'/clients',params={'clientId':'register-staff-portal'}).json()[0]['id']
role=next(x for x in s.get(base+'/clients/'+target+'/roles').json() if x['name']=='Intake Officer')
res=s.post(base+'/users/'+account['id']+'/role-mappings/clients/'+target,json=[role]);res.raise_for_status()
res=s.put(base+'/users/'+account['id'],json={'firstName':'NSIPA ODK','lastName':'Synchronization'});res.raise_for_status()
username='nsipa-odk-source-reader';email=username+'@demo.invalid'
users=s.get(base+'/users',params={'username':username,'exact':'true'}).json()
if not users:
 cfg['odk_password']=secrets.token_urlsafe(32);persist()
 res=s.post(base+'/users',json={'username':username,'email':email,'emailVerified':True,'firstName':'NSIPA ODK','lastName':'Source Reader','enabled':True,'credentials':[{'type':'password','value':cfg['odk_password'],'temporary':False}]});res.raise_for_status()
cfg['odk_username']=username;cfg['odk_origin']='https://odk.nigeriag2p.com';cfg['project_id']=1;cfg['forms']=['nsipa_field_household_demo','nsipa_household_mapping_check'];persist()
class Form(HTMLParser):
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='form' and 'action' in a:self.action=a['action']
odk=requests.Session();odk.verify='/opt/openg2p-lab/registration/ca-bundle.crt'
res=odk.get(cfg['odk_origin']+'/v1/oidc/login',timeout=30);f=Form();f.feed(res.text)
res=odk.post(f.action,data={'username':'admin','password':password,'credentialId':''},timeout=30);res.raise_for_status()
odk.headers['X-Requested-With']='XMLHttpRequest'
res=odk.get(cfg['odk_origin']+'/v1/users',timeout=30);res.raise_for_status();users=res.json()
actor=next((x for x in users if x['email']==email),None)
if not actor:
 res=odk.post(cfg['odk_origin']+'/v1/users',json={'email':email},timeout=30);res.raise_for_status();actor=res.json()
roles=odk.get(cfg['odk_origin']+'/v1/roles',timeout=30).json();print('ODK roles',[(x['id'],x.get('system')) for x in roles])
viewer=next(x for x in roles if x.get('system')=='viewer')
res=odk.post(cfg['odk_origin']+f"/v1/projects/1/assignments/{viewer['id']}/{actor['id']}",timeout=30)
if res.status_code!=409:res.raise_for_status()
token=requests.post(kc+'/realms/staff/protocol/openid-connect/token',data={'grant_type':'client_credentials','client_id':cid,'client_secret':cfg['client_secret']},timeout=30);token.raise_for_status()
ip=subprocess.check_output(['kubectl','-n','nigeria','get','svc','register-staff-portal-api','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
res=requests.post('http://'+ip+'/intake-form-data/get_intake_form_submissions_summary',headers={'Authorization':'Bearer '+token.json()['access_token'],'X-CSRF-Token':'sync-auth-probe'},cookies={'X-CSRF-Token':'sync-auth-probe'},json={'request_header':{'sender_app_mnemonic':'NSIPA_ODK_SYNC','sender_app_url':'https://odk.nigeriag2p.com','request_id':'probe','request_timestamp':'2026-11-10T00:00:00Z'},'request_body':{'request_payload':{'register_id':'a0000000-0000-4000-8000-000000000002','form_id':'c1000000-0000-4000-8000-000000000002'}}},timeout=30)
print('Registry service identity check',res.status_code,res.text[:400]);res.raise_for_status()
print('Provisioned dedicated intake-only service client and project-viewer ODK reader; private config saved.')




