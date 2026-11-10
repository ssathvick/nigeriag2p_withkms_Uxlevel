import requests,subprocess,yaml,json
from pathlib import Path
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
kc='http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password});r.raise_for_status();s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];base=kc+'/admin/realms/staff'
user=s.get(base+'/users',params={'username':'admin','exact':'true'}).json()[0]
out={'attributes':user.get('attributes'),'roles':s.get(base+'/users/'+user['id']+'/role-mappings').json(),'availableRoles':s.get(base+'/roles').json()}
Path(__file__).with_name('keycloak-role-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out)[:7000])
