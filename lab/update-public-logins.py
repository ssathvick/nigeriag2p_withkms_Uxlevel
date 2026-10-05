import requests,subprocess,json,pathlib,yaml,time,xmlrpc.client
R=pathlib.Path('/opt/openg2p-lab'); password=yaml.safe_load((R/'credentials.yaml').read_text())['admin_password']
def convert(s):return s.replace('beneficiary.openg2p-ux.localhost','beneficiary.nigeriag2p.com').replace('.openg2p.localhost','.nigeriag2p.com').replace('https://openg2p.localhost','https://nigeriag2p.com')
ip=subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True)
url='http://'+ip
for attempt in range(90):
 try:
  r=requests.post(url+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=5);r.raise_for_status();break
 except requests.RequestException:time.sleep(2)
else:raise RuntimeError('Keycloak unavailable')
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
for realm in ['staff','beneficiary']:
 endpoint=url+'/admin/realms/'+realm
 clients=s.get(endpoint+'/clients',timeout=20).json()
 backup=R/'public-domain-backup'/('keycloak-'+realm+'-clients.json')
 if not backup.exists():backup.write_text(json.dumps(clients));backup.chmod(0o600)
 for client in clients:
  before=json.dumps(client)
  # Retain the original local redirects as well as public redirect URIs.
  for field in ['redirectUris','webOrigins']:
   old=client.get(field,[]);client[field]=list(dict.fromkeys(old+[convert(v) for v in old]))
  for field in ['rootUrl','baseUrl','adminUrl']:
   if client.get(field):client[field]=convert(client[field])
  client['attributes']={k:convert(v) if isinstance(v,str) else v for k,v in client.get('attributes',{}).items()}
  if json.dumps(client)!=before:s.put(endpoint+'/clients/'+client['id'],json=client,timeout=20).raise_for_status()
 r=s.get(endpoint,timeout=20);r.raise_for_status();data=r.json()
 attrs=data.get('attributes',{});attrs['frontendUrl']='https://keycloak.nigeriag2p.com';data['attributes']=attrs
 s.put(endpoint,json=data,timeout=20).raise_for_status()
 print('Updated public OIDC redirects:',realm)
for host,db in [('pbms','pbmsdb'),('registry','socialregistrydb'),('portal-admin','portalpbmsdb')]:
 base='http://127.0.0.1:18080'
 sess=requests.Session();sess.headers['Host']=host+'.nigeriag2p.com'
 def call(path,params):
  r=sess.post(base+path,json={'jsonrpc':'2.0','method':'call','params':params,'id':1},timeout=30);r.raise_for_status();data=r.json()
  if 'error' in data:raise RuntimeError(data['error'].get('message','Odoo RPC error'))
  return data.get('result')
 for attempt in range(90):
  try:
   result=call('/web/session/authenticate',{'db':db,'login':'admin@nigeria.openg2p.localhost','password':password})
   if not result.get('uid'):raise RuntimeError('Odoo login failed')
   break
  except Exception:
   if attempt==89:raise
   time.sleep(2)
 for key,value in [('web.base.url','https://'+host+'.nigeriag2p.com'),('web.base.url.freeze','True')]:
  call('/web/dataset/call_kw/ir.config_parameter/set_param',{'model':'ir.config_parameter','method':'set_param','args':[key,value],'kwargs':{}})
 print('Updated Odoo base URL:',host)
print('Public application login settings updated.')
