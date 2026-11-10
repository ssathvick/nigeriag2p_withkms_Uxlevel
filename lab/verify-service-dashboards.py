"""Read-only HTTP checks for shared assets, entry routes and report authentication."""
import concurrent.futures,json
from pathlib import Path
from urllib.parse import urlparse,urljoin
import requests
src=Path(__file__).parent
modules=json.loads((src/'sitewide-ui/modules.json').read_text())
def check(m):
 url='https://'+m['host']+m['path']
 for _ in range(8):
  p=urlparse(url)
  if not(p.hostname=='g2p.wverve.in' or p.hostname.endswith('.nigeriag2p.com')):
   return {'service':m['id'],'error':'external redirect'}
  try:r=requests.get('http://127.0.0.1:18080'+p.path+('?' +p.query if p.query else ''),headers={'Host':p.hostname},allow_redirects=False,timeout=20)
  except requests.RequestException:return {'service':m['id'],'error':'request failed'}
  if r.is_redirect:url=urljoin(url,r.headers['Location']);continue
  return {'service':m['id'],'status':r.status_code,'shared_dashboard_assets':'service-insights.js' in r.text and 'site-shell.js' in r.text}
 return {'service':m['id'],'error':'redirect limit'}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 results=list(pool.map(check,modules))
for item in results:print(json.dumps(item))
for path in ['/registration/static/dashboard.js','/registration/static/dashboard.css','/iqs-brand/service-insights.js','/iqs-brand/service-insights.css']:
 r=requests.get('http://127.0.0.1:18080'+path,headers={'Host':'g2p.wverve.in'},timeout=10)
 assert r.status_code==200,path
r=requests.get('http://127.0.0.1:18081/registration/api/analytics',timeout=10)
assert r.status_code==401
(src/'sitewide-ui/dashboard-verification.json').write_text(json.dumps(results,indent=2))
assert all(x.get('status')==200 and x.get('shared_dashboard_assets') for x in results)
print('PASS: all service entry routes, dashboard assets, and anonymous report denial.')
