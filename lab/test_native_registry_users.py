import requests
import test_meeting_native_workflow as t
URL='https://g2p.wverve.in/registration/api/registry/users';ca='/opt/openg2p-lab/registration/ca-bundle.crt'
for email,expected in [('admin@openg2p.org',200),('aarin@gmail.com',403)]:
 s=t.session(email);token=next(c.value for c in s.cookies if c.name=='X-Access-Token');headers={'Authorization':'Bearer '+token};r=requests.get(URL,headers=headers,verify=ca,timeout=45);assert r.status_code==expected,(email,r.status_code)
 if expected==200:
  data=r.json();assert {u['email'] for u in data['users']}>=set(t.credentials);assert len(data['roles'])==5
  denied=requests.post(URL,headers=headers,json={'email':'invalid','role':'unrestricted-admin'},verify=ca,timeout=30);assert denied.status_code==400
 t.check('Native administrator directory reads five assigned staff and validates onboarding' if expected==200 else 'Officer cannot access staff administration')
