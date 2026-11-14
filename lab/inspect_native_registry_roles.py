import json,subprocess,requests,yaml
from pathlib import Path
from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
def service(name):return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
kc=service('commons-keycloak');password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];base=kc+'/admin/realms/staff'
client=s.get(base+'/clients',params={'clientId':'register-staff-portal'}).json()[0]
roles=s.get(base+'/clients/'+client['id']+'/roles').json()
print('Native registry client roles:',json.dumps([{'name':x['name'],'composite':x['composite'],'attributes':x.get('attributes')} for x in roles]))
for name in ['Intake Officer','Intake Validator']:
 role=next((x for x in roles if x['name']==name),None)
 if role:print(name,'composites',json.dumps(s.get(base+'/clients/'+client['id']+'/roles/'+name+'/composites').json()))
credentials=json.loads(Path('/mnt/h/Nigeria_Mosip/Credentials/mbr_demo_credentials.json').read_text())
old=json.loads(Path('/opt/openg2p-lab/registration/mbr-demo-credentials.json').read_text())
print('Supplied accounts:',json.dumps([{'email':k,'role':v.get('role'),'matches_current_password':v.get('password')==old.get(k,{}).get('password')} for k,v in credentials.items()]))
with connect('iam') as c:
 with c.cursor(cursor_factory=RealDictCursor) as cur:
  cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY 1");print('IAM tables:',[x['table_name'] for x in cur.fetchall()])
