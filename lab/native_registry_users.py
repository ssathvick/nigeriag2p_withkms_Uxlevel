"""Native Registry staff directory using the existing staff realm and IAM roles."""
import re,subprocess,requests,yaml
from pathlib import Path
from flask import request,abort,make_response
ROLES=['Registry Officer','Registry Field Agent','Registry First Reviewer','Registry Second Reviewer','Registry Administrator']
def install(module):
 app=module.app;prefix=module.PREFIX
 def authorize():
  def service(name):return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
  token=request.headers.get('Authorization','')
  if not token.startswith('Bearer '):abort(401)
  kc=service('commons-keycloak');r=requests.get(kc+'/realms/staff/protocol/openid-connect/userinfo',headers={'Authorization':token},timeout=20)
  if r.status_code!=200:abort(401)
  r=requests.get(service('commons-services-iam-staff-portal-api')+'/user-access/get_application_permissions_for_user',params={'application_mnemonic':'register-staff-portal'},headers={'Authorization':token},timeout=20);r.raise_for_status()
  if 'registryConfiguration:edit' not in {p for a in r.json() for p in a.get('permissions',[])}:abort(403)
  password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);r.raise_for_status();s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token'];base=kc+'/admin/realms/staff'
  r=s.get(base+'/clients',params={'clientId':'register-staff-portal'},timeout=20);r.raise_for_status();return s,base,r.json()[0]['id']
 @app.route(prefix+'/api/registry/users',methods=['GET','POST'])
 def users():
  s,base,client=authorize()
  try:
   if request.method=='POST':
    data=request.get_json(silent=True) or {};email=str(data.get('email') or '').strip().lower();name=str(data.get('name') or '').strip();role=data.get('role');password=data.get('temporary_password')
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email) or len(email)>254 or not name or len(name)>150 or role not in ROLES or not isinstance(password,str) or not 12<=len(password)<=128:return {'error':'Enter a valid name, email, registry role and temporary password of 12–128 characters.'},400
    r=s.get(base+'/users',params={'username':email,'exact':'true'},timeout=20);r.raise_for_status()
    if r.json():return {'error':'That account already exists. Its credentials and roles were preserved.'},409
    # Keep the identity disabled until all role grants have succeeded.
    r=s.post(base+'/users',json={'username':email,'email':email,'firstName':name,'enabled':False,'credentials':[{'type':'password','value':password,'temporary':True}],'requiredActions':['UPDATE_PASSWORD']},timeout=20);r.raise_for_status()
    uid=r.headers['Location'].rsplit('/',1)[-1]
    try:
     r=s.get(base+'/clients/'+client+'/roles/'+role,timeout=20);r.raise_for_status();s.post(base+'/users/'+uid+'/role-mappings/clients/'+client,json=[r.json()],timeout=20).raise_for_status()
     if role=='Registry Administrator':
      r=s.get(base+'/clients',params={'clientId':'iam-staff-ui'},timeout=20);r.raise_for_status();iam=r.json()[0]['id'];r=s.get(base+'/clients/'+iam+'/roles/IAM_ADMIN',timeout=20);r.raise_for_status();s.post(base+'/users/'+uid+'/role-mappings/clients/'+iam,json=[r.json()],timeout=20).raise_for_status()
     s.put(base+'/users/'+uid,json={'enabled':True},timeout=20).raise_for_status()
    except Exception:
     # A partially provisioned identity remains disabled; no passwords enter logs or responses.
     return {'error':'Account provisioning did not complete. The account remains disabled for administrator review.'},503
    return {'created':True,'email':email,'role':role,'password_change_required':True},201
   results=[]
   for role in ROLES:
    r=s.get(base+'/clients/'+client+'/roles/'+role+'/users',params={'max':1000},timeout=20);r.raise_for_status()
    for user in r.json():results.append({'email':user.get('email') or user['username'],'name':' '.join(filter(None,[user.get('firstName'),user.get('lastName')])),'role':role,'enabled':user.get('enabled',False)})
   response=make_response({'users':results,'roles':ROLES});response.headers['Cache-Control']='no-store, private';return response
  finally:s.close()
