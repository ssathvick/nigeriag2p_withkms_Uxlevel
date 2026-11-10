import requests,json,re,concurrent.futures
from bs4 import BeautifulSoup
from pathlib import Path
p=Path('territory-data/raw');s=BeautifulSoup((p/'lagos-members.html').read_text(),'html.parser');rows=[]
for h in s.select('h6'):
 name=h.get_text(' ',strip=True)
 if 'HON.' not in name:continue
 c=h.parent.parent;a=c.select_one('a[href]');role=c.select_one('p')
 rows.append(dict(state='Lagos',name=name,constituency=None,source_url=a['href'] if a else 'https://lagoshouseofassembly.gov.ng/home/our-team/',source_name='Lagos State House of Assembly',role=role.get_text(' ',strip=True) if role else None,note='Official current member directory checked 4 November 2026; publisher does not supply row-level effective dates.',chamber='State House of Assembly'))
assert len(rows)==40
def fetch(r):
 key=r['source_url'].rstrip('/').split('/')[-1]
 try:
  dest=p/('lagos-profile-'+key+'.html')
  if not dest.exists():
   resp=requests.get(r['source_url'],timeout=25);resp.raise_for_status();dest.write_text(resp.text)
  bs=BeautifulSoup(dest.read_text(),'html.parser');txt=bs.get_text(' ',strip=True)
  (p/('lagos-profile-'+key+'.txt')).write_text(txt)
  relevant=[x.get_text(' ',strip=True) for x in bs.select('p,h1,h2,h3,h4,h5,h6') if 'constituen' in x.get_text().lower()]
  print(r['name'],json.dumps(relevant))
 except Exception as e:print(r['name'],str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,rows))
(p/'lagos-officials-next.json').write_text(json.dumps(rows,indent=2))
