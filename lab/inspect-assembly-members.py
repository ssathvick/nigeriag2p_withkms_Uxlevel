import requests,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
p=Path('territory-data/raw')
urls={'imo-members':'https://imha.imostate.gov.ng/house-members/','ekiti-members':'https://www.hoa.ek.gov.ng/members','ekiti-bills':'https://www.hoa.ek.gov.ng/bills','fct-head':'https://aepb.fcta.gov.ng/','ogun-activities':'https://ogha.og.gov.ng/blog/'}
def get(it):
 k,u=it
 try:
  r=requests.get(u,timeout=25);r.raise_for_status();(p/(k+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');(p/(k+'.txt')).write_text(s.get_text(' ',strip=True));print(k,s.get_text(' ',strip=True)[:9000] if 'members' in k or 'bills' in k else 'downloaded')
 except Exception as e:print(k,e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(get,urls.items()))
for k in ['benue-assembly','osun-assembly','rivers-assembly','ondo-assembly']:
 print(k,(p/(k+'.txt')).read_text()[:9000])
