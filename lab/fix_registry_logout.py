"""Configure browser-reachable logout and exact allowed return URLs, preserving other clients."""
import json,datetime,subprocess,requests,yaml
from pathlib import Path
root=Path('/opt/openg2p-lab');backup=root/'registration/logout-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
def run(*args):return subprocess.check_output(args,text=True).strip()
deployment=json.loads(run('kubectl','-n','nigeria','get','deployment','register-staff-portal-ui','-o','json'));(backup/'deployment.json').write_text(json.dumps(deployment))
ip=run('kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}');base='http://'+ip;password=yaml.safe_load((root/'credentials.yaml').read_text())['admin_password']
r=requests.post(base+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);r.raise_for_status();s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
url=base+'/admin/realms/staff/clients';r=s.get(url,params={'clientId':'staff-portal'},timeout=20);r.raise_for_status();client=next(x for x in r.json() if x['clientId']=='staff-portal');p=backup/'staff-portal-client.json';p.write_text(json.dumps(client));p.chmod(0o600)
attrs=client.setdefault('attributes',{});values=[v for v in attrs.get('post.logout.redirect.uris','').split('##') if v]
for host in ['g2p-register.wverve.in','register.nigeriag2p.com']:
 for suffix in ['','/','/en']:
  value='https://'+host+suffix
  if value not in values:values.append(value)
attrs['post.logout.redirect.uris']='##'.join(values);r=s.put(url+'/'+client['id'],json=client,timeout=20);r.raise_for_status()
subprocess.run(['kubectl','-n','nigeria','set','env','deployment/register-staff-portal-ui','KEYCLOAK_LOGOUT_URL=https://g2p-keycloak.wverve.in/realms/staff/protocol/openid-connect/logout','COOKIE_DOMAIN=.wverve.in'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
print('Configured public logout and exact registry return URLs; private rollback backup saved')
