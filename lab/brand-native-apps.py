import subprocess,pathlib,yaml,xmlrpc.client,base64,json,requests
lab=pathlib.Path('/opt/openg2p-lab')
password=yaml.safe_load((lab/'credentials.yaml').read_text())['admin_password']
logo=base64.b64encode((lab/'branding/iqs-logo.png').read_bytes()).decode()
backup=lab/'branding-backup'; backup.mkdir(exist_ok=True)
def service(name):
 return 'http://'+subprocess.check_output(['kubectl','get','svc',name,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
for name,db in [('pbms-odoo','pbmsdb'),('registry-odoo','socialregistrydb'),('portal-backend-odoo','portalpbmsdb')]:
 url=service(name)
 uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(db,'admin@nigeria.openg2p.localhost',password,{})
 if not uid: raise RuntimeError('Login failed for '+name)
 proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
 def call(model,method,args,kw=None): return proxy.execute_kw(db,uid,password,model,method,args,kw or {})
 ids=call('res.company','search',[[]])
 previous=call('res.company','read',[ids,['name','logo']])
 target=backup/(name+'-company.json')
 if not target.exists(): target.write_text(json.dumps(previous));target.chmod(0o600)
 call('res.company','write',[ids,{'name':'IQS Nigeria G2P','logo':logo}])
 if call('ir.model','search',[[['model','=','website']]]):
  websiteids=call('website','search',[[]])
  if websiteids:call('website','write',[websiteids,{'name':'IQS Nigeria G2P'}])
 print(name,'company logo and name updated')
url=service('commons-keycloak')
r=requests.post(url+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
for realm,label in [('staff','IQS Nigeria — Staff'),('beneficiary','IQS Nigeria — Beneficiary'),('master','IQS Nigeria — Administration')]:
 endpoint=url+'/admin/realms/'+realm
 r=s.get(endpoint,timeout=20);r.raise_for_status();data=r.json()
 path=backup/(realm+'-realm-display.json')
 if not path.exists(): path.write_text(json.dumps({k:data.get(k) for k in ['displayName','displayNameHtml']}));path.chmod(0o600)
 r=s.put(endpoint,json={'displayName':label,'displayNameHtml':label},timeout=20);r.raise_for_status()
 print('Keycloak',realm,'display name updated')
