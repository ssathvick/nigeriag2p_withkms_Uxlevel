import requests
from pathlib import Path
from bs4 import BeautifulSoup
p=Path('territory-data/raw')
for k,u in [('cross-river-next','https://www.crshoa.crossriverstate.gov.ng/'),('delta-next','https://deltastategov.com.ng/portfolio/legislator/'),('ebonyi-next','https://ebonyistate.gov.ng/legislative.aspx'),('akwa-next','https://hoa.akwaibomstate.gov.ng/')]:
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();(p/(k+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');print(k,len(r.content),s.get_text(' ',strip=True)[-18000:]);(p/(k+'.txt')).write_text(s.get_text(' ',strip=True))
 except Exception as e: print(k,str(e)[:300])
