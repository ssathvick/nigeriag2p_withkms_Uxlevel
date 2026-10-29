import json, pathlib, secrets, subprocess, uuid, requests, yaml
ns=['kubectl','-n','nigeria']; runid=uuid.uuid4().hex[:12]
kc_ip=subprocess.check_output(ns+['get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}'],text=True).strip(); kc='http://'+kc_ip
pw=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':pw},timeout=15);r.raise_for_status()
admin=requests.Session(); admin.headers['Authorization']='Bearer '+r.json()['access_token']; realm=kc+'/admin/realms/beneficiary'
client='isolation-test-'+runid; users=[]; ids=[str(uuid.uuid4()),str(uuid.uuid4())]; names=['isolation-'+runid+'-a','isolation-'+runid+'-b']; secret=secrets.token_urlsafe(24); client_uuid=None
def pod(script):
 return subprocess.run(ns+['exec','-i','deploy/nigeria-consent-beneficiary-api','--','python','-'],input=script,text=True,check=True,capture_output=True)
try:
 r=admin.post(realm+'/clients',json={'clientId':client,'enabled':True,'publicClient':True,'directAccessGrantsEnabled':True,'standardFlowEnabled':False},timeout=15);r.raise_for_status()
 r=admin.get(realm+'/clients',params={'clientId':client},timeout=15);r.raise_for_status();client_uuid=r.json()[0]['id']
 for name in names:
  r=admin.post(realm+'/users',json={'username':name,'email':name+'@example.invalid','firstName':'Synthetic','lastName':'Test','enabled':True,'emailVerified':True,'credentials':[{'type':'password','value':secret,'temporary':False}]},timeout=15);r.raise_for_status()
  r=admin.get(realm+'/users',params={'username':name,'exact':'true'},timeout=15);r.raise_for_status();users.append(r.json()[0]['id'])
 script='''import asyncio,datetime\nfrom openg2p_consent_manager.main import app\nfrom openg2p_consent_manager.db import async_session\nfrom openg2p_consent_manager.models.consent import ConsentArtefact\nasync def go():\n async with async_session()() as s:\n  for ident,name in DATA:\n   now=datetime.datetime.now(datetime.timezone.utc)\n   s.add(ConsentArtefact(id=ident,subject_id_type="national_id",subject_id_value=name,controller_id="synthetic-test",partner_id="synthetic-test",purpose={"label":"fictional isolation test"},data_scopes=["demo"],effective_data_scopes=["demo"],fetch_type="oneshot",valid_from=now,valid_until=now+datetime.timedelta(days=1),source="embedded",status="active"))\n  await s.commit()\nasyncio.run(go())\n'''.replace('DATA',repr(list(zip(ids,names))))
 pod(script)
 token_url=kc+'/realms/beneficiary/protocol/openid-connect/token'
 for i,name in enumerate(names):
  r=requests.post(token_url,data={'grant_type':'password','client_id':client,'username':name,'password':secret},timeout=15)
  if not r.ok: raise RuntimeError('Test sign-in failed: '+str(r.json().get('error_description',r.status_code)))
  token=r.json()['access_token']
  headers={'Authorization':'Bearer '+token}; root='https://beneficiary-consent.nigeriag2p.com/consent/v1/my/consents'
  r=requests.get(root,headers=headers,timeout=15);r.raise_for_status(); visible={x['id'] for x in r.json()['items']}
  assert ids[i] in visible and ids[1-i] not in visible, 'list isolation failed'
  own=requests.get(root+'/'+ids[i],headers=headers,timeout=15);other=requests.get(root+'/'+ids[1-i],headers=headers,timeout=15)
  assert own.status_code==200 and other.status_code==404, f'detail isolation failed: {own.status_code}/{other.status_code}'
  print(f'Beneficiary {i+1}: own list and detail accessible; other record hidden (404).')
 print('ISOLATION TEST PASSED')
finally:
 cleanup='''import asyncio\nfrom openg2p_consent_manager.main import app\nfrom openg2p_consent_manager.db import async_session\nfrom openg2p_consent_manager.models.consent import ConsentArtefact\nfrom sqlalchemy import delete\nasync def go():\n async with async_session()() as s:\n  await s.execute(delete(ConsentArtefact).where(ConsentArtefact.id.in_(IDS),ConsentArtefact.controller_id=="synthetic-test"))\n  await s.commit()\nasyncio.run(go())\n'''.replace('IDS',repr(ids))
 try: pod(cleanup); print('Fictional test records removed.')
 finally:
  for uid in users: admin.delete(realm+'/users/'+uid,timeout=15).raise_for_status()
  if client_uuid: admin.delete(realm+'/clients/'+client_uuid,timeout=15).raise_for_status()
  print('Temporary test accounts and client removed.')
