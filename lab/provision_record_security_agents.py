"""Create five dedicated field identities; preserve other account passwords."""
from pathlib import Path
import json,secrets,subprocess,yaml,requests,os
from test_mbr_db_connection import connect
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
host=subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
kc='http://'+host;r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=30);r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];base=kc+'/admin/realms/staff'
r=s.get(base+'/clients',params={'clientId':'register-staff-portal'});r.raise_for_status();client=r.json()[0]['id']
r=s.get(base+'/clients/'+client+'/roles/Registry Field Agent');r.raise_for_status();role=r.json()
private=Path('/opt/openg2p-lab/registration/field-agent-accounts.json');accounts=json.loads(private.read_text()) if private.exists() else {}
for index in range(1,6):
 login=f'field-agent-{index:02}@nsipa.example.invalid';entry=accounts.get(login) or {'name':f'NSIPA Field Agent {index:02}','password':secrets.token_urlsafe(24)}
 r=s.get(base+'/users',params={'username':login,'exact':'true'});r.raise_for_status();found=r.json()
 if not found:
  r=s.post(base+'/users',json={'username':login,'email':login,'firstName':f'Field Agent {index:02}','lastName':'NSIPA','enabled':True,'emailVerified':True,'credentials':[{'type':'password','value':entry['password'],'temporary':False}]});r.raise_for_status()
  ident=r.headers['Location'].rsplit('/',1)[-1]
 else:
  ident=found[0]['id']
  if not found[0].get('lastName'):
   s.put(base+'/users/'+ident,json={'firstName':f'Field Agent {index:02}','lastName':'NSIPA','emailVerified':True}).raise_for_status()
 s.post(base+'/users/'+ident+'/role-mappings/clients/'+client,json=[role]).raise_for_status()
 entry.update(uid=ident,role='Registry Field Agent');accounts[login]=entry
 private.write_text(json.dumps(accounts,indent=2));private.chmod(0o600)
# Officer is a read-only consumer of fully approved field-origin records.
allowed={'register:view','registerDefinition:view','registerTab:view','registerSection:view','registerHistory:view','referenceData:view','intakeFormDefinition:view'}
with connect('iam') as c:
 with c.cursor() as q:
  q.execute("SELECT r.id FROM staff_roles r JOIN staff_portal_applications a ON a.id=r.application_id WHERE r.role_mnemonic='Registry Officer' AND a.application_mnemonic='register-staff-portal'");rid=q.fetchone()[0]
  q.execute('SELECT p.id,p.permission_mnemonic FROM staff_application_permissions p JOIN staff_roles r ON r.application_id=p.application_id WHERE r.id=%s AND p.active',(rid,));perms=q.fetchall()
  q.execute('UPDATE staff_role_permissions SET active=false,updated_at=now() WHERE role_id=%s',(rid,))
  for pid,mnemonic in perms:
   if mnemonic in allowed:
    q.execute('UPDATE staff_role_permissions SET active=true,updated_at=now() WHERE role_id=%s AND permission_id=%s',(rid,pid))
 c.commit()
export=os.environ.get('NSIPA_FIELD_CREDENTIAL_EXPORT')
copy=Path(export) if export else Path('/mnt/h/Nigeria_Mosip/Credentials/MBR-Field-Agents.json')
if copy.parent.exists():copy.write_text(private.read_text())
else:copy=private
print(json.dumps({'field_agents':len(accounts),'private_credentials':str(copy),'officer':'approved field-origin records, read only','passwords_printed':False}))
