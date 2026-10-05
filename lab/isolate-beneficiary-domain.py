import json,pathlib,subprocess,requests,yaml
old='beneficiary.openg2p.localhost';new='beneficiary.openg2p-ux.localhost'
def get(kind,name):return json.loads(subprocess.check_output(['kubectl','-n','nigeria','get',kind,name,'-o','json']))
for name in ['pbms-beneficiary-portal','pbms-beneficiary-portal-ui']:
 d=get('deploy',name)
 for c in d['spec']['template']['spec']['containers']:
  for e in c.get('env',[]):
   if 'value' in e:e['value']=e['value'].replace(old,new)
 subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':d['spec']['template']}})],check=True,stderr=subprocess.DEVNULL)
vss=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','vs','-o','json']))['items']
for vs in vss:
 if old in vs['spec']['hosts']:
  vs['spec']['hosts']=[h.replace(old,new) for h in vs['spec']['hosts']]
  subprocess.run(['kubectl','-n','nigeria','patch','vs',vs['metadata']['name'],'--type=merge','-p',json.dumps({'spec':vs['spec']})],check=True)
gateway=get('gateway','internal');gateway['spec']['servers'][0]['hosts'].append(new) if new not in gateway['spec']['servers'][0]['hosts'] else None
subprocess.run(['kubectl','-n','nigeria','patch','gateway','internal','--type=merge','-p',json.dumps({'spec':gateway['spec']})],check=True)
tls=pathlib.Path('/opt/openg2p-lab/tls');(tls/'extensions').write_text('subjectAltName=DNS:openg2p.localhost,DNS:*.openg2p.localhost,DNS:'+new+'\nextendedKeyUsage=serverAuth\n')
subprocess.run(['openssl','x509','-req','-in',str(tls/'server.csr'),'-CA',str(tls/'ca.crt'),'-CAkey',str(tls/'ca.key'),'-CAcreateserial','-out',str(tls/'server.crt'),'-days','825','-extfile',str(tls/'extensions')],check=True,stderr=subprocess.DEVNULL)
p=pathlib.Path('/etc/nginx/sites-available/openg2p-lab');text=p.read_text();text=text.replace('server_name *.openg2p.localhost;','server_name *.openg2p.localhost '+new+';');p.write_text(text)
subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/bootstrap-portal.py').read().split("call('ir.module.module','update_list'")[0])
providers=call('auth.oauth.provider','search_read',[[['name','=','Local UX Demo Login']]])
for provider in providers:
 changes={k:v.replace(old,new) for k,v in provider.items() if isinstance(v,str) and old in v};call('auth.oauth.provider','write',[[provider['id']],changes])
kc_ip=subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip();kc='http://'+kc_ip
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password});r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];realm=kc+'/admin/realms/beneficiary'
client=s.get(realm+'/clients',params={'clientId':'nigeria-beneficiary-portal'}).json()[0];client['redirectUris']=['https://'+new+'/*'];client['webOrigins']=['https://'+new]
s.put(realm+'/clients/'+client['id'],json=client).raise_for_status()
print('Beneficiary portal isolated from staff SSO cookies:',new)
