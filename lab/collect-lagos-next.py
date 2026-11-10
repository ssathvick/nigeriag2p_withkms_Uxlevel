import requests,json,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
p=Path('territory-data/raw')
urls={'lagos-members':'https://lagoshouseofassembly.gov.ng/home/our-team/', 'lagos-land-review':'https://lagoshouseofassembly.gov.ng/home/lagos-assembly-adopts-commt-recommendations-on-igbaro-oteshade-royal-family-land-excision/','lagos-wealth-review':'https://lagoshouseofassembly.gov.ng/home/lagos-assembly-adopts-commt-recommendations-on-wealth-fund-bill-2025/'}
def fetch(k,u):
 try:
  r=requests.get(u,timeout=35);r.raise_for_status();(p/(k+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');(p/(k+'.txt')).write_text(s.get_text(' ',strip=True));print(k,s.get_text(' ',strip=True)[-16000:])
 except Exception as e:print(k,e)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(lambda it:fetch(*it),urls.items()))
