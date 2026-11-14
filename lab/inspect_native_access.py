import sys,json
from pathlib import Path
from test_mbr_db_connection import connect
exec((Path(__file__).parent/'client-concerns/inspect_demo_roles.py').read_text().split('user=s.get')[0])
client=s.get(base+'/clients',params={'clientId':'register-staff-portal'}).json()[0]
print('client', {k:client.get(k) for k in ['clientId','directAccessGrantsEnabled']})
for appname in ['iam-staff-ui']:
 appclient=s.get(base+'/clients',params={'clientId':appname}).json()[0]
 print('administration roles',appname,[r['name'] for r in s.get(base+'/clients/'+appclient['id']+'/roles').json()])
for email in json.loads(Path('/mnt/h/Nigeria_Mosip/Credentials/mbr_demo_credentials.json').read_text()):
 users=s.get(base+'/users',params={'search':email,'exact':'true'}).json()
 print('account',email,[(u['username'],u.get('enabled'),[r['name'] for r in s.get(base+'/users/'+u['id']+'/role-mappings/clients/'+client['id']).json()]) for u in users])
with connect('iam') as c:
 with c.cursor() as q:
  for table in ['staff_roles','staff_role_permissions','staff_users','staff_user_roles','staff_portal_applications']:
   q.execute('select column_name,data_type,column_default from information_schema.columns where table_name=%s order by ordinal_position',(table,));print(table,q.fetchall())
  q.execute('select id,application_mnemonic from staff_portal_applications');print('applications',q.fetchall())
with connect('awe') as c:
 with c.cursor() as q:
  q.execute("select p.policy_key,p.version,p.status,s.stage_order,r.rule_type,r.rule_value from approval_policy p join approval_stage s on s.policy_id=p.id join approver_rule r on r.stage_id=s.id where p.policy_key like 'registry.%' and p.status='active' order by 1,2,4");print('policies',q.fetchall())
with connect() as c:
 with c.cursor() as q:
  q.execute('select state,native_origin,count(*) from g2p_mbr_submissions group by 1,2');print('supplemental states',q.fetchall())
  q.execute("select id,reference,state,native_origin from g2p_mbr_submissions where state not in ('APPROVED','REJECTED','CANCELLED')");print('unresolved',q.fetchall())
  q.execute("select created_by,created_at,source,title,jsonb_object_keys(payload) from g2p_mbr_submissions where native_origin is null");print('draft metadata',q.fetchall())
