"""Fresh HTTP SSO sessions, real cookie jar and authenticated identity checks."""
import json
from pathlib import Path
from urllib.parse import urlparse
import test_location_import_e2e as e
e.HOST='https://g2p-register.wverve.in'
def verify():
 accounts=json.loads(Path('/opt/openg2p-lab/registration/client-demo-accounts.json').read_text())
 results=[]
 for name in ['nsipa-demo-reviewer-one','nsipa-demo-reviewer-two']:
  s=e.login(e.HOST,name,accounts[name]['password'])
  cookies=[{'name':c.name,'domain':c.domain,'secure':c.secure,'path':c.path} for c in s.cookies if c.name.startswith('X-')]
  assert any(c['name']=='X-Access-Token' and c['domain']=='.wverve.in' for c in cookies)
  assert all(c['secure'] for c in cookies)
  for attempt in range(2):
   response=s.get(e.HOST+'/api/me',timeout=30)
   assert response.status_code==200, 'Authenticated identity HTTP '+str(response.status_code)
   identity=response.json()
   assert name in json.dumps(identity),'Unexpected authenticated reviewer'
  results.append({'reviewer':name,'origin':e.HOST,'fresh_login':True,'authenticated_identity_checks':2,'cookies':cookies})
  s.close()
 path=Path(__file__).parent/'wverve-reviewer-login-results.json';path.write_text(json.dumps(results,indent=2))
 print(json.dumps(results,indent=2))
if __name__=='__main__':verify()
