import requests,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw')
urls={'adamawa-planning-next':'https://adspc.ad.gov.ng/state-legislative-council/','zamfara-speaker-next':'https://molga.zamfara.gov.ng/speaker/'}
def get(k,u):
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();(P/(k+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');(P/(k+'.txt')).write_text(s.get_text(' ',strip=True));print(k,s.get_text(' ',strip=True)[-14000:]);print('links',[(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]') if any(t in a.get_text().lower() for t in ['member','representative'])])
 except Exception as e:print(k,e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(lambda p:get(*p),urls.items()))
