from bs4 import BeautifulSoup
from pathlib import Path
import requests,re,collections,json
p=Path('territory-data/raw')
for key in ['naltf-senators','naltf-reps']:
 s=BeautifulSoup((p/(key+'.html')).read_text(),'html.parser');cards=s.select('.fg-layout-3-item-content');print(key,len(cards));print([x.get_text(' ',strip=True) for x in cards][-12:])
 if not cards:print([str(x.parent)[:1000] for x in s.select('h2') if 'Aguocha' in x.get_text()])
u='https://billtracker.naltf.gov.ng/assets/index-DwyQwnUc.js';r=requests.get(u,timeout=40);(p/'naltf-bills.js').write_text(r.text)
print('api clues',re.findall(r'.{0,90}(?:https://|/api/|supabase).{0,130}',r.text)[:40])
s=BeautifulSoup((p/'ogun-members.html').read_text(),'html.parser');a=s.select('.team-card-content a')[0];u=a['href'];r=requests.get(u,timeout=30);(p/'ogun-profile-example.html').write_text(r.text);print('OGUN',BeautifulSoup(r.text,'html.parser').get_text(' ',strip=True)[-8000:])
