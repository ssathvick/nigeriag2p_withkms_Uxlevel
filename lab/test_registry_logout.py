"""Live authenticated logout redirect, cookie cleanup and SSO checks on both registry domains."""
import sys,json
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
creds=json.loads(Path('/mnt/h/Nigeria_Mosip/Credentials/mbr_demo_credentials.json').read_text())
results=[]
for origin in ['https://g2p-register.wverve.in','https://register.nigeriag2p.com']:
 s=login(origin,'aarin@gmail.com',creds['aarin@gmail.com']['password'])
 assert any(c.name=='X-Access-Token' for c in s.cookies),'Login cookie missing'
 r=s.get(origin+'/api/logout',allow_redirects=False,timeout=30)
 assert r.status_code in [302,303,307,308],r.status_code
 target=r.headers['Location'];host=urlparse(target).hostname
 print('Logout cookie scopes:',[(c.name,c.domain,c.path,c.expires) for c in s.cookies if c.name.startswith('X-')],flush=True)
 print('Expiry header scopes:',[(line.split(';')[1:]) for line in r.raw.headers.getlist('Set-Cookie')],flush=True)
 assert host in ['g2p-keycloak.wverve.in','keycloak.nigeriag2p.com'],host
 r=s.get(target,timeout=30)
 if not r.ok:
  import re
  message=re.search(r'<(?:span|p)[^>]*class="[^"]*(?:kc-feedback-text|instruction)[^"]*"[^>]*>(.*?)</(?:span|p)>',r.text,re.S)
  raise RuntimeError('Logout HTTP '+str(r.status_code)+': '+(re.sub('<[^>]+>','',message.group(1)).strip() if message else 'Identity provider rejected logout'))
 assert all(urlparse(x.url).hostname not in ['commons-keycloak','localhost'] for x in [*r.history,r])
 assert urlparse(r.url).hostname==urlparse(origin).hostname,('Incorrect return host',urlparse(r.url).hostname)
 assert not any(c.name in ['X-Access-Token','X-ID-Token'] and (urlparse(origin).hostname==c.domain.lstrip('.') or urlparse(origin).hostname.endswith('.'+c.domain.lstrip('.'))) for c in s.cookies),'Auth cookies survived logout'
 again=s.get(origin+'/api/login?redirect_uri='+origin+'/en',timeout=30);again.raise_for_status()
 assert 'kc-form-login' in again.text,'SSO session survived logout'
 result={'origin':origin,'status':'passed','publicLogoutHost':host,'returnHost':urlparse(r.url).hostname,'authCookiesCleared':True,'freshLoginRequired':True}
 results.append(result);print('PASS logout redirect, cleared cookies and fresh sign-in: '+origin,flush=True)
 s.close()
out=ROOT.parent/'output/logout-verification';out.mkdir(exist_ok=True);(out/'results.json').write_text(json.dumps({'status':'passed','results':results},indent=2))
