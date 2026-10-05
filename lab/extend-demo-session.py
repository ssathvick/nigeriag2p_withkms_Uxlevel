import pathlib,subprocess,requests,yaml
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
ip=subprocess.check_output(['kubectl','get','svc','commons-keycloak','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
url='http://'+ip
r=requests.post(url+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password});r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
r=s.get(url+'/admin/realms/beneficiary');r.raise_for_status();realm=r.json();realm['accessTokenLifespan']=3600
s.put(url+'/admin/realms/beneficiary',json=realm).raise_for_status()
print('Local beneficiary demo token lifetime: one hour')
