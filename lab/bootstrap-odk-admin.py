import pathlib,yaml,subprocess,requests
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
ip=subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip();kc='http://'+ip
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password});r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
user=s.get(kc+'/admin/realms/staff/users',params={'username':'admin','exact':'true'}).json()[0]
email=user['email']
for action in ['user-create','user-promote']:
 r=subprocess.run(['kubectl','-n','nigeria','exec','deploy/commons-services-odk-central-backend','--','node','/usr/odk/lib/bin/cli.js','-u',email,action],text=True,capture_output=True)
 print(action,r.returncode,r.stdout[-300:],r.stderr[-300:])
 if r.returncode and 'already' not in r.stderr:raise RuntimeError('ODK account setup failed')
