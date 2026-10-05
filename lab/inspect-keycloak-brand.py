exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/brand-native-apps.py').read().split("for name,db in")[0])
url=service('commons-keycloak')
r=requests.post(url+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
for c in s.get(url+'/admin/realms/staff/clients').json():
 if any('staff-portal.openg2p.localhost' in uri for uri in c.get('redirectUris',[])):
  print(json.dumps({k:c.get(k) for k in ['clientId','redirectUris','name']}))
