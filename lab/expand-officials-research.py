import requests
from bs4 import BeautifulSoup
from pathlib import Path
for key,u in [('ngf-governors','https://ngf.org.ng/'),('kwara-assembly','https://hoa.kw.gov.ng/10th-assembly-members/')]:
 try:
  r=requests.get(u,timeout=25);r.raise_for_status();Path('territory-data/raw/'+key+'.html').write_text(r.text);s=BeautifulSoup(r.text,'html.parser');print(key,s.get_text(' ',strip=True)[:1200]);print([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]') if 'governor' in a.get_text().lower()][:35])
 except Exception as e:print(key,e)
