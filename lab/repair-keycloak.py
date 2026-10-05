import subprocess,json,pathlib,yaml,requests,base64
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
ip=subprocess.check_output(['kubectl','get','svc','commons-keycloak','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
url='http://'+ip
response=requests.post(url+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20)
response.raise_for_status(); session=requests.Session();session.headers['Authorization']='Bearer '+response.json()['access_token']
realm=url+'/admin/realms/staff'
client_id='openg2p-g2p-bridge-nigeria'
clients=session.get(realm+'/clients',params={'clientId':client_id}).json()
if not clients:
    r=session.post(realm+'/clients',json={'clientId':client_id,'enabled':True,'serviceAccountsEnabled':True,'standardFlowEnabled':False,'publicClient':False});r.raise_for_status()
    clients=session.get(realm+'/clients',params={'clientId':client_id}).json()
secret=session.get(realm+'/clients/'+clients[0]['id']+'/client-secret').json()['value']
resource={'apiVersion':'v1','kind':'Secret','metadata':{'name':client_id,'namespace':'nigeria'},'type':'Opaque','stringData':{'client_secret':secret}}
subprocess.run(['kubectl','apply','-f','-'],input=yaml.safe_dump(resource),text=True,check=True,stdout=subprocess.DEVNULL)
for client in session.get(realm+'/clients').json():
    if not client.get('serviceAccountsEnabled'):continue
    role=session.get(realm+'/clients/'+client['id']+'/roles/Admin')
    if role.status_code!=200:continue
    account=session.get(realm+'/clients/'+client['id']+'/service-account-user').json()
    response=session.post(realm+'/users/'+account['id']+'/role-mappings/clients/'+client['id'],json=[role.json()])
    print('Service account role',client['clientId'],response.status_code)
print('Bridge authentication secret initialized.')
