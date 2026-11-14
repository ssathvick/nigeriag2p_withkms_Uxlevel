from pathlib import Path
from bs4 import BeautifulSoup
import json,base64,collections,re,requests,concurrent.futures
p=Path('territory-data/raw');records=[]
for key,chamber in [('naltf-senators','Senate'),('naltf-reps','House of Representatives')]:
 s=BeautifulSoup((p/(key+'.html')).read_text(),'html.parser');e=s.select_one('[data-gallery-items]');cards=[BeautifulSoup(x,'html.parser').select_one('.fg-layout-3-item-content') for x in json.loads(base64.b64decode(e['data-gallery-items']))] if e else s.select('.fg-layout-3-item-content')
 for c in cards:
  name=c.select_one('h2').get_text(' ',strip=True);t=c.select_one('.fg-item-content').get_text(' ',strip=True);records.append({'name':name,'chamber':chamber,'raw':t})
 print(key,len(cards))
(p/'representative-roster-extracted.json').write_text(json.dumps(records,indent=2));print('lastsen', [x for x in records if x['chamber']=='Senate'][-6:])
b=json.loads((p/'naltf-bills.json').read_text());print('bills',len(b),'sponsors',collections.Counter(x.get('sponsorName') for x in b).most_common(20));print('sample',[x for x in b if x.get('sponsorName') not in ['Unknown Sponsor',None]][:2]);print('statuses',collections.Counter(x.get('status') for x in b))
s=BeautifulSoup((p/'ogun-members.html').read_text(),'html.parser')
def get(a):
 u=a['href'];h=requests.get(u,timeout=35).text;file='ogun-member-'+u.rsplit('/',1)[1]+'.html';(p/file).write_text(h);t=BeautifulSoup(h,'html.parser').get_text(' ',strip=True);m=re.search(r'Constituency:\s*(.*?)\s*(?:Email:|Biography|Activities)',t);return {'name':a.get_text(' ',strip=True),'constituency':m[1] if m else None,'url':u,'role':a.parent.parent.select_one('p').get_text(' ',strip=True)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:ogun=list(pool.map(get,s.select('.team-card-content a')))
(p/'ogun-members.json').write_text(json.dumps(ogun,indent=2));print('ogun',len(ogun),ogun)
