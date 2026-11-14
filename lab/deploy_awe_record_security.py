from pathlib import Path
import subprocess,json,datetime,requests,yaml
from psycopg2 import sql
from test_mbr_db_connection import connect
from record_security_secret import signing_environment
root=Path(__file__).parent/'record-security'
def run(*args,input=None):return subprocess.check_output(args,input=input,text=True,stderr=subprocess.PIPE)
ip=run('kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}').strip()
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];r=requests.post('http://'+ip+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=30);r.raise_for_status();s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];base='http://'+ip+'/admin/realms/staff'
r=s.get(base+'/clients',params={'clientId':'register-staff-portal'});r.raise_for_status();client=r.json()[0]['id'];r=s.get(base+'/clients/'+client+'/roles/Registry Field Agent/users',params={'max':1000});r.raise_for_status();agents=r.json()
r=s.get(base+'/clients',params={'clientId':'nsipa-odk-registry-sync'});r.raise_for_status();sync_client=r.json()[0]['id']
r=s.get(base+'/clients/'+sync_client+'/service-account-user');r.raise_for_status();sync_subject=r.json()['id']
r=s.get(base+'/clients/'+client+'/roles/Registry Administrator/users',params={'max':1000});r.raise_for_status();admins=r.json()
with connect() as c:
 with c.cursor() as q:
  q.execute((root/'schema.sql').read_text())
  q.execute('DELETE FROM nsipa_security.field_actors')
  q.execute('DELETE FROM nsipa_security.registry_admins')
  for admin in admins:q.execute('INSERT INTO nsipa_security.registry_admins VALUES(%s)',(admin['id'],))
  for agent in agents:q.execute('INSERT INTO nsipa_security.field_actors VALUES(%s,%s)',(agent['id'],agent['username']))
 c.commit()
run('kubectl','-n','nigeria','set','env','deployment/register-staff-portal-api','NSIPA_ODK_SERVICE_SUB='+sync_subject)
with connect('awe') as c:
 with c.cursor() as q:
  q.execute((root/'awe-schema.sql').read_text())
  for agent in agents:
   for subject in [agent['id'],agent['username']]:q.execute('INSERT INTO nsipa_security.field_actors VALUES(%s) ON CONFLICT DO NOTHING',(subject,))
  # Resolve the service database role without reading or printing a password.
  code="import os,json;print(json.dumps({k:v for k,v in os.environ.items() if 'DB' in k and ('USERNAME' in k or k.endswith('_USER'))}))"
  users=json.loads(run('kubectl','-n','nigeria','exec','deploy/commons-services-awe','--','python','-c',code))
  if len(set(users.values()))!=1:raise RuntimeError('Cannot determine the AWE database role')
  user=next(iter(users.values()));q.execute(sql.SQL('GRANT nsipa_awe_scoped TO {}').format(sql.Identifier(user)))
 c.commit()
d=json.loads(run('kubectl','-n','nigeria','get','deploy','commons-services-awe','-o','json'))
backup=Path('/opt/openg2p-lab/registration/record-security-backups')/('awe-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700);(backup/'deployment.json').write_text(json.dumps(d))
files={'scope':('awe_scope.py','awe/record_scope.py'),'main':('awe-main.py','awe/main.py'),'auth':('awe-auth.py','awe/services/auth.py'),'task':('awe-task.py','awe/controllers/task.py'),'request':('awe-request.py','awe/controllers/request.py')}
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nsipa-awe-record-security','namespace':'nigeria'},'data':{k:(root/src).read_text() for k,(src,target) in files.items()}}
run('kubectl','apply','-f','-',input=json.dumps(cm));spec=d['spec']['template']['spec'];container=spec['containers'][0];prefix='/usr/local/lib/python3.13/site-packages/';targets={prefix+t for src,t in files.values()}
container['env']=[e for e in container.get('env',[]) if e['name']!='NSIPA_ODK_SERVICE_SUB']+[{'name':'NSIPA_ODK_SERVICE_SUB','value':sync_subject}]
signing_environment(container)
spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!='nsipa-awe-record-security']+[{'name':'nsipa-awe-record-security','configMap':{'name':'nsipa-awe-record-security'}}]
container['volumeMounts']=[m for m in container.get('volumeMounts',[]) if m['name']!='nsipa-awe-record-security' and m['mountPath'] not in targets]+[{'name':'nsipa-awe-record-security','mountPath':prefix+target,'subPath':key,'readOnly':True} for key,(src,target) in files.items()]
d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['nsipa-record-security']=datetime.datetime.now().isoformat()
run('kubectl','replace','-f','-',input=json.dumps(d));print(run('kubectl','-n','nigeria','rollout','status','deployment/commons-services-awe','--timeout=240s'))
print('AWE record isolation deployed; Registry field identities:',len(agents))
