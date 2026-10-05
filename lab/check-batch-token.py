exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/seed-platform-batch.py').read().split('states=')[0])
kc=svc('commons-keycloak')
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password});r.raise_for_status()
ks=requests.Session();ks.headers['Authorization']='Bearer '+r.json()['access_token']
c=ks.get(kc+'/admin/realms/staff/clients',params={'clientId':'awe-admin-portal'}).json()[0]
secret=ks.get(kc+'/admin/realms/staff/clients/'+c['id']+'/client-secret').json().get('value','')
r=requests.post(kc+'/realms/staff/protocol/openid-connect/token',data={'client_id':c['clientId'],'client_secret':secret,'grant_type':'password','username':'admin','password':password});r.raise_for_status()
api=requests.get(svc('commons-services-pm-staff-portal-api')+'/partners',headers={'Authorization':'Bearer '+r.json()['access_token']});print('PM access via existing AWE client:',api.status_code)
