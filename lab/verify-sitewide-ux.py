import requests,concurrent.futures,json
from pathlib import Path
from urllib.parse import urlparse,urljoin
source=Path(__file__).parent;modules=json.loads((source/'sitewide-ui/modules.json').read_text());results=[]
def inspect(m):
 u='https://'+m['host']+m['path'];visited=[]
 try:
  for _ in range(6):
   p=urlparse(u)
   if not (p.hostname=='g2p.wverve.in' or p.hostname.endswith('.nigeriag2p.com')):return {'module':m['id'],'error':'redirect outside platform'}
   visited.append(p.hostname+p.path)
   r=requests.get('http://127.0.0.1:18080'+p.path+('?' +p.query if p.query else ''),headers={'Host':p.hostname},timeout=20,allow_redirects=False)
   if r.is_redirect:u=urljoin(u,r.headers['Location']);continue
   return {'module':m['id'],'status':r.status_code,'html':'text/html' in r.headers.get('content-type',''),'ux_assets':'site-shell.js?v=sitewide-20261005-r2' in r.text,'destination':p.hostname+p.path}
  return {'module':m['id'],'error':'too many redirects'}
 except Exception as e:return {'module':m['id'],'error':type(e).__name__}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(inspect,modules))
(source/'sitewide-ui/verification.json').write_text(json.dumps(results,indent=2))
for item in results:print(json.dumps(item))
assert all(item.get('status')==200 and item.get('html') and item.get('ux_assets') for item in results),'Some module entry pages need attention'
for asset in ['site.js','site.css','site-shell.js','site-shell.css']:
 r=requests.get('http://127.0.0.1:18080/iqs-brand/'+asset,headers={'Host':'g2p.wverve.in'},timeout=10);assert r.status_code==200
print('PASS: module entry pages and four shared assets')
