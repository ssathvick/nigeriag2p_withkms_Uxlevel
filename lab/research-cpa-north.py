import requests,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw')
states=['adamawa','borno','kaduna','katsina','kebbi','nasarawa','niger','plateau','sokoto','yobe','zamfara']
def get(st):
 try:
  u='https://www.cpahq.org/directory/'+st+'/'
  r=requests.get(u,timeout=15);r.raise_for_status();s=BeautifulSoup(r.text,'html.parser');t=s.get_text(' ',strip=True);(P/('cpa-'+st+'.html')).write_text(r.text);(P/('cpa-'+st+'.txt')).write_text(t)
  i=t.find('CPA '+st.title());print(st,t[max(0,i-150):i+150] if i>=0 else t[-1500:])
 except Exception as e:print(st,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(get,states))
