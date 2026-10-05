import subprocess,requests,pathlib,yaml,json,sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
ip=lambda s:subprocess.check_output(['kubectl','get','svc',s,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
kc='http://'+ip('commons-keycloak')
master=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password});master.raise_for_status()
ks=requests.Session();ks.headers['Authorization']='Bearer '+master.json()['access_token'];kr=kc+'/admin/realms/staff'
user=ks.get(kr+'/users',params={'username':'admin','exact':'true'}).json()[0]
for role in ['AWE_ADMIN','AWE_VIEWER']:
 if ks.get(kr+'/roles/'+role).status_code==404:ks.post(kr+'/roles',json={'name':role}).raise_for_status()
 ks.post(kr+'/users/'+user['id']+'/role-mappings/realm',json=[ks.get(kr+'/roles/'+role).json()]).raise_for_status()
client=ks.get(kr+'/clients',params={'clientId':'awe-admin-portal'}).json()[0]
client['directAccessGrantsEnabled']=True
ks.put(kr+'/clients/'+client['id'],json=client).raise_for_status()
secret=ks.get(kr+'/clients/'+client['id']+'/client-secret').json().get('value','')
r=requests.post(kc+'/realms/staff/protocol/openid-connect/token',data={'client_id':client['clientId'],'client_secret':secret,'grant_type':'password','username':'admin','password':password});r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];awe='http://'+ip('commons-services-awe')+'/v1/awe'
tasks=query('awe',"SELECT id FROM approval_task WHERE request_id='700ca35f-d97d-4f6d-84e5-3be9d3a75049' AND status='open';").splitlines()
for task in tasks:
 if query('awe',"SELECT assignee FROM approval_task WHERE id='"+task+"';").strip()!='admin':
  r=s.post(awe+'/tasks/'+task+'/reassign',json={'new_assignee':'admin','reason':'Local synthetic UX workflow verification'});print('Reassign',r.status_code,r.text[:300]);r.raise_for_status();task=r.json()['id']
 r=s.post(awe+'/tasks/'+task+'/decision',json={'action':'approve','comment':'Synthetic middle-name edit approved for local UX verification'});print('Decision',r.status_code,r.text[:300]);r.raise_for_status()
print(query('awe',"SELECT status FROM approval_request WHERE id='700ca35f-d97d-4f6d-84e5-3be9d3a75049';"))
