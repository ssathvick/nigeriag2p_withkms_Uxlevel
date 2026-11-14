import requests,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
urls={'ngf-current':'https://ngf.org.ng/index.php/the-ngf/governors','abia-assembly':'https://abiastate.gov.ng/house-of-assembly/','adamawa-assembly':'https://adspc.ad.gov.ng/adamawa-state-house-of-assembly-legisture/'}
def get(item):
 k,u=item
 try:
  r=requests.get(u,timeout=30);r.raise_for_status();Path('territory-data/raw/'+k+'.html').write_text(r.text);s=BeautifulSoup(r.text,'html.parser');print(k,s.get_text(' ',strip=True)[-18000:])
 except Exception as e:print(k,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(get,urls.items()))
