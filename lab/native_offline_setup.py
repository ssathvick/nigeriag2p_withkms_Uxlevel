"""Authenticated Collect setup utility for the native Master Registry (no intake engine)."""
import base64,io,json,subprocess,zlib
from pathlib import Path
from html.parser import HTMLParser
import requests,yaml,qrcode,qrcode.image.svg
from flask import request,abort,make_response
def install(module):
 app=module.app;prefix=module.PREFIX
 @app.post(prefix+'/api/registry/offline-setup')
 def setup():
  token=request.headers.get('Authorization','')
  if not token.startswith('Bearer '):abort(401)
  def service(name):return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
  kc=service('commons-keycloak')
  identity=requests.get(kc+'/realms/staff/protocol/openid-connect/userinfo',headers={'Authorization':token},timeout=20)
  if identity.status_code!=200:abort(401)
  user=identity.json();username=user.get('preferred_username')
  if not username:abort(403)
  permissions=requests.get(service('commons-services-iam-staff-portal-api')+'/user-access/get_application_permissions_for_user',params={'application_mnemonic':'register-staff-portal'},headers={'Authorization':token},timeout=20)
  permissions.raise_for_status();allowed={p for item in permissions.json() for p in item.get('permissions',[])}
  if 'intakeSubmission:edit' not in allowed:abort(403)
  password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
  origin='https://g2p-odk.wverve.in';session=requests.Session();session.verify='/opt/openg2p-lab/registration/ca-bundle.crt'
  class Form(HTMLParser):
   def handle_starttag(self,tag,attrs):
    data=dict(attrs)
    if tag=='form' and 'action' in data:self.action=data['action']
  response=session.get(origin+'/v1/oidc/login',timeout=30);response.raise_for_status();form=Form();form.feed(response.text)
  response=session.post(form.action,data={'username':'admin','password':password,'credentialId':''},timeout=30);response.raise_for_status()
  session.headers['X-Requested-With']='XMLHttpRequest'
  response=session.get(origin+'/v1/projects/1/app-users',timeout=30);response.raise_for_status()
  label='Registry field capture · '+username
  account=next((u for u in response.json() if u.get('displayName')==label and u.get('token')),None)
  if not account:
   response=session.post(origin+'/v1/projects/1/app-users',json={'displayName':label},timeout=30);response.raise_for_status();account=response.json()
  response=session.get(origin+'/v1/roles',timeout=30);response.raise_for_status();role=next(r for r in response.json() if r.get('system')=='app-user')
  forms=['nsipa_registry_household']
  for fid in forms:
   response=session.post(origin+f"/v1/projects/1/forms/{fid}/assignments/{role['id']}/{account['id']}",timeout=30)
   if response.status_code!=409:response.raise_for_status()
  settings={'project':{'name':'NSIPA Master Registry','color':'#155e50'},'general':{'server_url':origin+'/v1/key/'+account['token']+'/projects/1','autosend':'wifi_and_cellular','delete_send':False,'default_completed':False,'metadata_username':username,'form_update_mode':'previously_downloaded','automatic_update':True},'admin':{}}
  payload=base64.b64encode(zlib.compress(json.dumps(settings).encode())).decode()
  image=qrcode.make(payload,image_factory=qrcode.image.svg.SvgPathImage,box_size=5,border=4);buffer=io.BytesIO();image.save(buffer)
  try:session.delete(origin+'/v1/sessions/current',timeout=10)
  finally:session.close()
  response=make_response({'qr_svg':'data:image/svg+xml;base64,'+base64.b64encode(buffer.getvalue()).decode(),'account':username,'forms':forms,'auto_send':'wifi_and_cellular','retains_sent_records':True})
  response.headers['Cache-Control']='no-store, private';return response
