exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/bootstrap-portal.py').read())
odoo_call=call
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/repair-keycloak.py').read())
beneficiary_realm=url+'/admin/realms/beneficiary'
if session.get(beneficiary_realm).status_code==404:
 session.post(url+'/admin/realms',json={'realm':'beneficiary','enabled':True,'displayName':'Nigeria Beneficiary UX Lab','sslRequired':'external'}).raise_for_status()
client_id='nigeria-beneficiary-portal'
clients=session.get(beneficiary_realm+'/clients',params={'clientId':client_id}).json()
if not clients:
 session.post(beneficiary_realm+'/clients',json={'clientId':client_id,'enabled':True,'standardFlowEnabled':True,'publicClient':False,'redirectUris':['https://beneficiary.openg2p.localhost/*'],'webOrigins':['https://beneficiary.openg2p.localhost']}).raise_for_status()
 clients=session.get(beneficiary_realm+'/clients',params={'clientId':client_id}).json()
secret=session.get(beneficiary_realm+'/clients/'+clients[0]['id']+'/client-secret').json()['value']
users=session.get(beneficiary_realm+'/users',params={'username':'fatima','exact':'true'}).json()
if not users:
 session.post(beneficiary_realm+'/users',json={'username':'fatima','enabled':True,'emailVerified':True,'firstName':'Fatima','lastName':'Abubakar','email':'fatima@example.invalid'}).raise_for_status()
 users=session.get(beneficiary_realm+'/users',params={'username':'fatima','exact':'true'}).json()
session.put(beneficiary_realm+'/users/'+users[0]['id']+'/reset-password',json={'type':'password','value':password,'temporary':False}).raise_for_status()
call=odoo_call
def upsert(model,domain,values):
 ids=call(model,'search',[domain])
 if ids:call(model,'write',[ids,values]);return ids[0]
 return call(model,'create',[values])
id_type=upsert('g2p.id.type',[['name','=','Local UX Identity']],{'name':'Local UX Identity'})
for value in ['Female','Male','Other']:
 upsert('gender.type',[['value','=',value]],{'value':value,'code':value})
partner=upsert('res.partner',[['ref','=','NG-PORTAL-0001']],{'name':'Fatima Abubakar','given_name':'Fatima','family_name':'Abubakar','ref':'NG-PORTAL-0001','email':'fatima@example.invalid','gender':'Female','birthdate':'1980-01-15','is_registrant':True,'is_group':False,'country_id':country,'company_id':1})
upsert('g2p.reg.id',[['value','=',users[0]['id']],['id_type','=',id_type]],{'value':users[0]['id'],'id_type':id_type,'partner_id':partner})
issuer='https://keycloak.openg2p.localhost/realms/beneficiary'
provider=upsert('auth.oauth.provider',[['name','=','Local UX Demo Login']],{'name':'Local UX Demo Login','body':'Sign in to local demo','enabled':True,'g2p_self_service_allowed':True,'flow':'oidc_auth_code','auth_endpoint':issuer+'/protocol/openid-connect/auth','token_endpoint':issuer+'/protocol/openid-connect/token','jwks_uri':issuer+'/protocol/openid-connect/certs','validation_endpoint':issuer+'/protocol/openid-connect/userinfo','client_id':client_id,'client_secret':secret,'client_authentication_method':'client_secret_post','scope':'openid profile email','enable_pkce':True,'token_map':'sub:user_id name:name email:email','g2p_id_type':id_type,'company_id':1,'date_format':'%Y-%m-%d','g2p_portal_oauth_callback_url':'https://beneficiary.openg2p.localhost/v1/selfservice/oauth2/callback'})
program=upsert('g2p.program',[['name','=','Nigeria Household Support — Portal UX Demo']],{'name':'Nigeria Household Support — Portal UX Demo','description':'Synthetic Nigeria programme for beneficiary journey design. No live payment or government eligibility policy.','active':True})
fields=call('g2p.program','fields_get',[],{'attributes':['selection']})
print('Programme status choices',fields.get('state',{}))
api_ip=subprocess.check_output(['kubectl','get','svc','pbms-beneficiary-portal','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
r=requests.get('http://'+api_ip+'/v1/selfservice/openapi.json');
if r.status_code==200:
 pathlib.Path('/opt/openg2p-lab/beneficiary-openapi.json').write_text(r.text)
 print('OAuth routes',[p for p in r.json()['paths'] if 'oauth' in p])
print('Portal programme and synthetic beneficiary seeded. Login username: fatima')

