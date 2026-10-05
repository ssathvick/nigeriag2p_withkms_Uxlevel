exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/repair-keycloak.py').read())
users=session.get(realm+'/users',params={'username':'admin','exact':'true'}).json()
for user in users:
 user['requiredActions']=[];user['emailVerified']=True
 session.put(realm+'/users/'+user['id'],json=user).raise_for_status()
 session.put(realm+'/users/'+user['id']+'/reset-password',json={'type':'password','value':password,'temporary':False}).raise_for_status()
 for client in session.get(realm+'/clients').json():
  roles=session.get(realm+'/clients/'+client['id']+'/roles').json()
  if roles:
   response=session.post(realm+'/users/'+user['id']+'/role-mappings/clients/'+client['id'],json=roles)
   response.raise_for_status()
 print('Local staff administrator enabled with application roles.')
# Upstream partner-management service account initialization expects this role.
clients=session.get(realm+'/clients',params={'clientId':'commons-services-staff-portal'}).json()
if clients:
 c=clients[0];r=session.get(realm+'/clients/'+c['id']+'/roles/partner_manager')
 if r.status_code==404:
  session.post(realm+'/clients/'+c['id']+'/roles',json={'name':'partner_manager'}).raise_for_status()
 role=session.get(realm+'/clients/'+c['id']+'/roles/partner_manager').json()
 for c2 in session.get(realm+'/clients').json():
  if 'partner' not in c2['clientId'] or not c2.get('serviceAccountsEnabled'):continue
  account=session.get(realm+'/clients/'+c2['id']+'/service-account-user').json()
  session.post(realm+'/users/'+account['id']+'/role-mappings/clients/'+c['id'],json=[role]).raise_for_status()
print('Staff access bootstrap complete.')
