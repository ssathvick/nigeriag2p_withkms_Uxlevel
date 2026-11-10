import requests,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
root=Path('territory-data/raw')
urls={'naltf-senators':'https://naltf.gov.ng/members-of-the-senate/','naltf-home':'https://naltf.gov.ng/','nass-reps':'https://www.nass.gov.ng/mps/representatives','ogun-members':'https://www.ogha.og.gov.ng/members','lagos-members':'https://lagoshouseofassembly.gov.ng/'}
def get(item):
 key,url=item
 try:
  r=requests.get(url,timeout=40);r.raise_for_status();(root/(key+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');(root/(key+'.txt')).write_text(s.get_text(' ',strip=True));print(key,r.status_code)
  if key in ['naltf-home','lagos-members']:print([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]') if any(x in (a.get_text()+a.get('href','')).lower() for x in ['member','representative','bill'])][:40])
 except Exception as e: print(key,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(get,urls.items()))
