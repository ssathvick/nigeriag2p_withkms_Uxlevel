"""Configure supplied identities in native Registry IAM and AWE; preserve history."""
import datetime,json,subprocess,uuid
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import Json
from test_mbr_db_connection import connect
import argparse,os,requests,yaml
parser=argparse.ArgumentParser(description='Configure native Registry roles and versioned AWE review policies for existing destination identities; passwords are preserved.')
parser.add_argument('--accounts',type=Path,required=True)
parser.add_argument('--apply',action='store_true')
args=parser.parse_args()
credentials=json.loads(args.accounts.read_text())
valid={'mbr-officer','mbr-field-agent','mbr-level1','mbr-level2','mbr-admin'}
if not credentials or any(v.get('role') not in valid for v in credentials.values()):parser.error('Invalid or empty registry account role mapping')
reviewers={}
for role in ['mbr-level1','mbr-level2']:
 matches=[email for email,v in credentials.items() if v['role']==role]
 if len(matches)!=1:parser.error('Supply one distinct identity for each reviewer stage')
 reviewers[role]=matches[0]
print(json.dumps({'accounts':len(credentials),'roles':sorted({v['role'] for v in credentials.values()}),'apply':args.apply}))
if not args.apply:raise SystemExit(0)
password=yaml.safe_load(Path(os.environ.get('PBMS_CREDENTIALS_FILE','/opt/openg2p-lab/credentials.yaml')).read_text())['admin_password']
host=subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
response=requests.post('http://'+host+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=30);response.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+response.json()['access_token'];base='http://'+host+'/admin/realms/staff'

root=Path('/opt/openg2p-lab/registration')
backup=root/'native-account-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,mode=0o700)

client=s.get(base+'/clients',params={'clientId':'register-staff-portal'}).json()[0]['id']
read={'register:view','registerDefinition:view','registerTab:view','registerSection:view','registerHistory:view','referenceData:view','intakeFormDefinition:view','intakeSubmission:view','changeRequest:view','verificationIntakeForm:view','verificationChangeRequest:view'}
permissions={
 'mbr-officer':read|{'intakeSubmission:edit','changeRequest:create','register:authenticate'},
 'mbr-field-agent':read|{'intakeSubmission:edit'},
 'mbr-level1':read|{'intakeSubmission:approve','verificationIntakeForm:view','verificationIntakeForm:create','verificationChangeRequest:view','verificationChangeRequest:create'},
 'mbr-level2':read|{'intakeSubmission:approve','verificationIntakeForm:view','verificationIntakeForm:create','verificationChangeRequest:view','verificationChangeRequest:create'},
 'mbr-admin':read|{'registryConfiguration:view','registryConfiguration:edit','registerScore:view','register:export'},
}
names={'mbr-officer':'Registry Officer','mbr-field-agent':'Registry Field Agent','mbr-level1':'Registry First Reviewer','mbr-level2':'Registry Second Reviewer','mbr-admin':'Registry Administrator'}
account_backup=[]
with connect('iam') as c:
 with c.cursor() as q:
  q.execute('SELECT id FROM staff_portal_applications WHERE application_mnemonic=%s',('register-staff-portal',));app=q.fetchone()[0]
  q.execute('SELECT id,permission_mnemonic FROM staff_application_permissions WHERE application_id=%s AND active',(app,));available={name:id for id,name in q.fetchall()}
  for key,allowed in permissions.items():
   missing=allowed-available.keys()
   if missing:raise RuntimeError('Unknown native permissions: '+str(missing))
   name=names[key]
   role=s.get(base+'/clients/'+client+'/roles/'+name)
   if role.status_code==404:
    s.post(base+'/clients/'+client+'/roles',json={'name':name,'description':'Native master registry: '+name}).raise_for_status()
   else:role.raise_for_status()
   q.execute('SELECT id FROM staff_roles WHERE application_id=%s AND role_mnemonic=%s',(app,name));found=q.fetchone()
   if found:rid=found[0]
   else:
    q.execute('INSERT INTO staff_roles(role_mnemonic,role_description,application_id,active,created_at,updated_at) VALUES(%s,%s,%s,true,now(),now()) RETURNING id',(name,'Native master registry '+name,app));rid=q.fetchone()[0]
   q.execute('UPDATE staff_role_permissions SET active=false,updated_at=now() WHERE role_id=%s',(rid,))
   for permission in sorted(allowed):
    pid=available[permission]
    q.execute('SELECT id FROM staff_role_permissions WHERE role_id=%s AND permission_id=%s',(rid,pid));existing=q.fetchone()
    if existing:q.execute('UPDATE staff_role_permissions SET active=true,updated_at=now() WHERE id=%s',(existing[0],))
    else:q.execute('INSERT INTO staff_role_permissions(role_id,permission_id,active,created_at,updated_at) VALUES(%s,%s,true,now(),now())',(rid,pid))
 c.commit()
for email,config in credentials.items():
 users=s.get(base+'/users',params={'username':email,'exact':'true'}).json()
 if len(users)!=1:raise RuntimeError('Expected established identity: '+email)
 user=users[0];uid=user['id'];role_name=names[config['role']]
 assigned=s.get(base+'/users/'+uid+'/role-mappings/clients/'+client);assigned.raise_for_status()
 account_backup.append({'user':user,'native_roles':assigned.json()})
 (backup/'accounts.json').write_text(json.dumps(account_backup));(backup/'accounts.json').chmod(0o600)
 wrong=[r for r in assigned.json() if r['name']!=role_name]
 if wrong:s.delete(base+'/users/'+uid+'/role-mappings/clients/'+client,json=wrong).raise_for_status()
 role=s.get(base+'/clients/'+client+'/roles/'+role_name).json()
 s.post(base+'/users/'+uid+'/role-mappings/clients/'+client,json=[role]).raise_for_status()
 # Preserve existing passwords, enabled status and required actions.
 if config['role']=='mbr-admin':
  iam=s.get(base+'/clients',params={'clientId':'iam-staff-ui'}).json()[0]['id']
  iam_role=s.get(base+'/clients/'+iam+'/roles/IAM_ADMIN');iam_role.raise_for_status()
  s.post(base+'/users/'+uid+'/role-mappings/clients/'+iam,json=[iam_role.json()]).raise_for_status()

# Version policies rather than editing stages referenced by historical requests.
with connect('awe') as c:
 with c.cursor() as q:
  q.execute("SELECT id,policy_key,version FROM approval_policy WHERE status='active' AND policy_key LIKE 'registry.%' ORDER BY policy_key")
  for old,key,version in q.fetchall():
   q.execute('SELECT s.stage_order,r.rule_value FROM approval_stage s JOIN approver_rule r ON r.stage_id=s.id WHERE s.policy_id=%s ORDER BY s.stage_order',(old,))
   if q.fetchall()==[(1,{'user_id':reviewers['mbr-level1']}),(2,{'user_id':reviewers['mbr-level2']})]:continue
   fresh=str(uuid.uuid4())
   q.execute("INSERT INTO approval_policy(id,policy_key,version,name,description,status,artifact_type,created_by,forbid_self_approval,forbid_repeat_approvers,created_at,updated_at) SELECT %s,policy_key,%s,name,'Native Registry independent first and second review','active',artifact_type,'native-registry-role-integration',true,true,now(),now() FROM approval_policy WHERE id=%s",(fresh,version+1,old))
   q.execute('SELECT id,stage_order FROM approval_stage WHERE policy_id=%s ORDER BY stage_order',(old,))
   for sid,order in q.fetchall():
    if order not in [1,2]:raise RuntimeError('Unexpected approval stage')
    stage=str(uuid.uuid4())
    q.execute('INSERT INTO approval_stage(id,policy_id,stage_order,name,mode,mode_value,sla_hours,parallel_group,skip_if,on_empty,on_breach,escalation_rules_json,created_at,updated_at) SELECT %s,%s,stage_order,name,mode,mode_value,sla_hours,parallel_group,skip_if,on_empty,on_breach,escalation_rules_json,now(),now() FROM approval_stage WHERE id=%s',(stage,fresh,sid))
    q.execute("INSERT INTO approver_rule(id,stage_id,rule_type,rule_value,kind,required,created_at,updated_at) VALUES(%s,%s,'user',%s,'approver',false,now(),now())",(str(uuid.uuid4()),stage,Json({'user_id':reviewers['mbr-level1'] if order==1 else reviewers['mbr-level2']})))
   q.execute("UPDATE approval_policy SET status='retired',updated_at=now() WHERE id=%s",(old,))
 c.commit()
print(json.dumps({'accounts':[{ 'email':e,'native_role':names[v['role']]} for e,v in credentials.items()],'backup':str(backup),'passwords_exposed':False}))
