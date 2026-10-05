exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/repair-keycloak.py').read())
client_id='register-staff-portal'
client=session.get(realm+'/clients',params={'clientId':client_id}).json()[0]
secret=session.get(realm+'/clients/'+client['id']+'/client-secret').json()['value']
r=requests.post(url+'/realms/staff/protocol/openid-connect/token',data={'grant_type':'client_credentials','client_id':client_id,'client_secret':secret});r.raise_for_status()
template=pathlib.Path('/opt/openg2p-lab/charts/openg2p-registry/files/iam-registration/payload.json').read_text()
for old,new in {'__APPLICATION_MNEMONIC__':client_id,'__APPLICATION_URL__':'https://register.openg2p.localhost','__API_URL__':'https://staff-register.openg2p.localhost','__APPLICATION_DESCRIPTION__':'Nigeria Social Registry'}.items():template=template.replace(old,new)
iam_ip=subprocess.check_output(['kubectl','get','svc','commons-services-iam-staff-portal-api','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
res=requests.post('http://'+iam_ip+'/user-access/staff_portal_applications',headers={'Authorization':'Bearer '+r.json()['access_token']},json=json.loads(template),timeout=45)
print('Registry IAM registration',res.status_code,res.text[:500]);res.raise_for_status()
# Regenerate Keycloak roles and administrator mappings after IAM self-registration.
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/finish-access.py').read())
