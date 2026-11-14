from bs4 import BeautifulSoup
from pathlib import Path
import requests
p=Path('territory-data/raw')
for key in ['naltf-senators','ogun-members','nass-reps']:
 s=BeautifulSoup((p/(key+'.html')).read_text(),'html.parser')
 print('\n',key)
 if key=='naltf-senators':
  h=next(h for h in s.select('h2') if 'Akobundu' in h.get_text());print(str(h.parent)[:5000])
 elif key=='ogun-members':
  h=next(h for h in s.select('h4') if 'Elemide' in h.get_text());print(str(h.parent)[:4000]);print([(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]') if 'member' in a.get('href','')][:10])
 else:print(s.get_text(' ',strip=True)[-7000:])
for key,url in [('naltf-reps','https://naltf.gov.ng/honorable-members/'),('naltf-bills','https://billtracker.naltf.gov.ng/')]:
 r=requests.get(url,timeout=40);(p/(key+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');(p/(key+'.txt')).write_text(s.get_text(' ',strip=True));print(key,s.get_text(' ',strip=True)[:9000]);print('scripts',[a.get('src') for a in s.select('script[src]')])
