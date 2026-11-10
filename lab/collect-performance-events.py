from pathlib import Path
from bs4 import BeautifulSoup
import requests,concurrent.futures,json
p=Path('territory-data/raw');s=BeautifulSoup((p/'ogun-activities.html').read_text(),'html.parser')
terms=['begins oversight visit','financial documents','diversity, inclusion commission','2026 budget defence']
urls={}
for a in s.select('a[href]'):
 if any(t in a.get_text().lower() for t in terms):urls[a['href'].strip('/') .split('/')[-1]]=a['href']
def get(it):
 k,u=it
 try:
  r=requests.get(u,timeout=25);r.raise_for_status();(p/(k+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');main=s.select_one('article') or s;txt=main.get_text(' ',strip=True);(p/(k+'.txt')).write_text(txt);print(k,txt[:9000])
 except Exception as e:print(k,e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,urls.items()))
