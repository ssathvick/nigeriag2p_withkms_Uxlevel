exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-keycloak-brand.py').read().split('for c in')[0])
realm=url+'/admin/realms/staff'
users=s.get(realm+'/users',params={'username':'admin','exact':'true'}).json()
for user in users:
 print('User',json.dumps({k:user.get(k) for k in ['id','username','email','enabled','requiredActions']}))
 print('Lockout',s.get(realm+'/attack-detection/brute-force/users/'+user['id']).json())
print('Recent login events',s.get(realm+'/events',params={'max':6,'type':'LOGIN_ERROR'}).json())
for client in ['admin-cli','awe-admin-portal']:
 r=requests.post(url+'/realms/staff/protocol/openid-connect/token',data={'client_id':client,'grant_type':'password','username':'admin','password':password},timeout=20)
 print('Credential check',client,r.status_code,'SUCCESS' if r.status_code==200 else r.json().get('error_description'))
