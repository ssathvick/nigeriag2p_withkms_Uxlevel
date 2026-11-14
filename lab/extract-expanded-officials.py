"""Extract factual directory fields from reviewed official publisher snapshots."""
import json,re
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw');rows=[]
def soup(key):return BeautifulSoup((P/(key+'.html')).read_text(),'html.parser')
def add(state,name,seat,url,publisher,role=None,note=None,office='State House of Assembly'):
 rows.append({'state':state,'name':name.strip(),'constituency':seat.strip() if seat else None,'source_url':url,'source_name':publisher,'role':role,'note':note,'chamber':office})
# Governor names only: never copy arbitrary page/footer HTML.
for card in soup('ngf-current').select('.magazine-item-main'):
 a=card.select_one('h3 a')
 if not a or 'State Governor' not in a.get_text():continue
 state=a.get_text(' ',strip=True).replace(' State Governor','').replace('Akwa-Ibom','Akwa Ibom')
 text=card.get_text(' ',strip=True);name=text.split('State Governor',1)[1].removeprefix(' Details').strip()
 add(state,name,state,'https://ngf.org.ng'+a['href'],'Nigeria Governors’ Forum',role='Governor',office='Governor',note='NGF governor directory checked 4 November 2026; party and term-end dates are not inferred. Source does not provide a row-level update date.')
assert sum(x['chamber']=='Governor' for x in rows)==36
assert 'Nyesom Wike' in soup('fct-head').get_text(' ',strip=True)
add('Federal Capital Territory','Ezenwo Nyesom Wike','Federal Capital Territory','https://aepb.fcta.gov.ng/','Abuja Environmental Protection Board / FCTA',role='FCT Minister · appointed',office='FCT Minister (appointed)',note='Appointed federal minister, not an elected governor. FCT has no State House of Assembly; its elected National Assembly representatives are listed separately.')
for c in soup('kwara-assembly').select('.tmm_textblock'):
 add('Kwara',c.select_one('.tmm_names').get_text(' ',strip=True),c.select_one('.tmm_desc').get_text(' ',strip=True),'https://hoa.kw.gov.ng/10th-assembly-members/','Kwara State House of Assembly',c.select_one('.tmm_job').get_text(' ',strip=True))
for c in soup('ekiti-members').select('.team-card-content'):
 ps=c.select('p');a=c.select_one('h4 a')
 if not a:continue
 add('Ekiti',a.get_text(' ',strip=True),ps[-1].get_text(' ',strip=True),'https://www.hoa.ek.gov.ng/members','Ekiti State House of Assembly',ps[0].get_text(' ',strip=True),note='7th Assembly directory. The publisher leaves one seat as “Ekiti East” without its division; no division is inferred.')
for c in soup('imo-members').select('.ova-info-content'):
 a=c.select_one('a.name');p=c.select_one('.job')
 if not a or not p:continue
 desc=p.get_text(' ',strip=True);role=None;seat=desc
 if not ('Constituency' in desc or 'Ideato' in desc or 'Owerri' in desc):role=desc;seat=None
 add('Imo',a.get_text(' ',strip=True),seat,'https://imha.imostate.gov.ng/house-members/','Imo State House of Assembly',role,note='Six leadership cards do not supply constituencies; seats remain unverified. Stale profile URL slugs are not used as identity evidence.')
for c in soup('osun-assembly').select('.allphoto'):
 vals=list(c.select_one('a').stripped_strings)
 add('Osun',vals[0],vals[-1].strip('() '),'https://osha.osunstate.gov.ng/allmembers','Osun State House of Assembly',vals[1],note='8th Assembly directory. The source repeats Ilesa East for two members; both are flagged rather than silently corrected.')
for c in soup('benue-assembly').select('.bb-person'):
 name=c.select_one('.bb-person-name');meta=c.select_one('.bb-person-meta');role=c.select_one('.bb-person-role')
 if not name:continue
 add('Benue',name.get_text(' ',strip=True),meta.get_text(' ',strip=True).split('·')[0].strip() if meta else None,'https://mio.benuestate.gov.ng/about-benue/house-of-assembly','Benue Ministry of Information and Orientation',role.get_text(' ',strip=True) if role else None,note='Official source repeats Makurdi North for two named members; no unique occupant is asserted for that label.')
# Publisher embeds the roster as a literal JavaScript array; parse fields, do not execute source scripts.
text=(P/'ondo-assembly.html').read_text();block=text.split('const assemblyMembers = [',1)[1].split('];',1)[0]
for c in re.findall(r'\{(.*?)\}',block,re.S):
 values=dict(re.findall(r'(name|constituency|position):\s*"([^"]*)"',c));assert set(values)=={'name','constituency','position'}
 add('Ondo',values['name'],values['constituency'],'https://www.ondostate.gov.ng/house_members','Ondo State Government',values['position'],note='Constituency divisions reproduced as supplied; several publisher labels omit a division. No LGA allocation is inferred.')
for c in soup('rivers-assembly').select('h3'):
 name=c.get_text(' ',strip=True)
 if not re.match(r'(?:Rt\.|Hon\.)',name):continue
 p=c.find_next_sibling('p');desc=p.get_text(' ',strip=True) if p else '';seat=None
 m=re.search(r'\((.*?)\)|House Member\s*-\s*(.*)',desc)
 if m:seat=m[1] or m[2]
 add('Rivers',name,seat,'https://riversstate.gov.ng/government/legislature','Rivers State Government',desc if not desc.startswith('House Member') else 'Member',note='Partial official leadership/member roster. No unlisted seats or tenure dates inferred.')
# Oyo: verified public web text; preserve leadership names without inventing seats.
text=(P/'assembly-web-evidence.txt').read_text()
for line in text.splitlines():
 m=re.match(r'L(?:9[4-9]|100|10[4-9]|11[0-9]|12[0-8]): (.*?)\s*\|\s*(.*)',line)
 if not m:continue
 name,desc=m.groups();seat=re.sub(r'\s*\([^)]*\)\s*[Mm]ember.*','',desc).strip() if 'Member' in desc or 'member' in desc else None
 add('Oyo',name.rstrip('\\'),seat,'https://oyostate.gov.ng/the-legislature/','Oyo State Government',None if seat else desc,note='Leadership table does not state constituencies for its seven principal officers; these remain unverified.')
assert sum(x['state']=='Kwara' and x['chamber']=='State House of Assembly' for x in rows)==24
assert sum(x['state']=='Ekiti' and x['chamber']=='State House of Assembly' for x in rows)==26
assert sum(x['state']=='Imo' and x['chamber']=='State House of Assembly' for x in rows)==27
assert sum(x['state']=='Osun' and x['chamber']=='State House of Assembly' for x in rows)==26
assert sum(x['state']=='Ondo' and x['chamber']=='State House of Assembly' for x in rows)==26
assert sum(x['state']=='Oyo' and x['chamber']=='State House of Assembly' for x in rows)==32
(P/'expanded-officials.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
from collections import Counter
print(Counter((x['state'],x['chamber']) for x in rows));print('total',len(rows))
