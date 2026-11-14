import test_meeting_native_workflow as t
import requests
for email,expected in [('abuchi@gmail.com',200),('abutu@gmail.com',403)]:
 s=t.session(email);token=next(c.value for c in s.cookies if c.name=='X-Access-Token')
 r=requests.post('https://g2p.wverve.in/registration/api/registry/offline-setup',headers={'Authorization':'Bearer '+token},verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=60)
 assert r.status_code==expected,('Offline setup status',email,r.status_code,r.text[:120])
 if expected==200:
  data=r.json();assert data['qr_svg'].startswith('data:image/svg+xml;base64,');assert data['auto_send']=='wifi_and_cellular';assert data['account']==email
 print('PASS','Private field QR and automatic-send configuration' if expected==200 else 'Reviewer cannot provision field capture')
