import json,re
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw');rows=[]
def add(state,name,seat,url,publisher,role=None,note='Official directory snapshot checked 4 November 2026; source supplies no row-level effective dates.'):
 rows.append(dict(state=state,name=name,constituency=seat,source_url=url,source_name=publisher,role=role,note=note,chamber='State House of Assembly'))
s=BeautifulSoup((P/'jigawa-next.html').read_text(),'html.parser')
for c in s.select('.team-content'):
 h=c.find(['h2','h3']);p=c.find('p')
 if not h and p and p.get_text().strip().startswith('Hon.'):
  h=p;p=p.find_next_sibling('p')
 if not h or not p:continue
 name=h.get_text(' ',strip=True);desc=p.get_text(' ',strip=True)
 m=re.search(r'\((.*?) Constituency\)',desc,re.I)
 seat=m[1] if m else re.sub(r'\s+Constituency.*','',desc,flags=re.I)
 role=desc.split('(')[0].strip(' -') if m else 'Member'
 add('Jigawa',name,seat,'https://jigawastate.gov.ng/housemembers','Jigawa State Government',role,note='Official directory checked 4 November 2026. Publisher abbreviations and apparent truncated names are retained; no missing name expansion, tenure dates, party changes or geographic allocation inferred.')
assert len(rows)==30,len(rows)
text='''Lawal Tini|Ajingi
Musa Tahir Haruna|Albasu
Ali Lawan Alhassan|Bagwai/Shanono
Ali Muhammad Tiga|Bebeji
Lawal Shehu|Bichi
Hafiz Gambo|Bunkure
Lawal Husain|Dala
Murtala Musa Kore|Danbatta
Rabiu Shuaibu|Dawakin Kudu
Saleh Ahmad Marke|Dawakin Tofa
Salisu Ibrahim Muhammad|Doguwa
Tukur Mohammed|Fagge
Zakariyya Abdullahi Nuhu|Gabasawa
Murtala Muhammad Kadage|Garko
Abubakar Danladi Isah|Gaya
Abdullahi Yahya|Gezawa
Abdulmajid Isah Umar|Gwale
Yunusa Haruna Kayyu|Gwarzo
Ayuba Labaran Alhassan|Kabo
Sarki Aliyu Daneji|Kano Municipal
Engr Ahmad Ibrahim|Karaye
Garba Shehu Fammar|Kibiya
Usman Abubakar Tasi’u|Kiru
Mudassir Ibrahim|Kumbotso
Garba Ya’u Gwarmai|Tsanyawa/Ghari
Alhassan Zakari Ishaq|Kura/Garun Malam
Suleiman Mukhtar Ishaq|Madobi
Ahmad Muhammad|Makoda
Abdul Abdulhamid|Minjibir
Yusuf Bello Aliyu|Nassarawa
Muhammad Ibrahim|Rano
Muhammad Bello Butu-butu|Rimin gado/Tofa
Jibril Ismail Falgore|Rogo
Zubairu Hamza Masu|Sumaila
Musa Ali Kachako|Takai
Kabiru Sule Dahiru|Tarauni
Sule Lawal Shuwaki|Tudun Wada
Aminu Sa’ad|Ungogo
Labaran Abdul Madari|Warawa
Ali Abdullahi Manager|Wudil'''
for line in text.splitlines():
 name,seat=line.split('|');role={'Dala':'Majority leader','Rimin gado/Tofa':'Deputy Speaker','Rogo':'Speaker','Warawa':'Minority leader'}.get(seat,'Member')
 add('Kano','Hon. '+name,seat,'https://kanoassembly.gov.ng/10th-kano-state-house-of-assembly-members-2023-2027/','Kano State House of Assembly',role,note='10th Assembly 2023–2027 roster reviewed via search-indexed official page on 4 November 2026 (direct page returned 403). Explicitly deceased 2023–2024 member Kundila is excluded; Ali Lawan Alhassan is labelled 2025–2027 by publisher. Generic /member page contains stale names and is not used. No row-level update dates or party changes inferred.')
assert len(rows)==70
add('Bauchi','Rt. Hon. Dr. Abubakar Y. Suleiman',None,'https://home.bauchistate.gov.ng/legislative/','Bauchi State Government','Speaker',note='Official leadership page reviewed through search-indexed publisher content; constituency not supplied. Partial leadership-only coverage, not a complete assembly roster.')
add('Bauchi','Hon. Jamilu Umaru Dahiru',None,'https://home.bauchistate.gov.ng/legislative/','Bauchi State Government','Deputy Speaker',note='Official leadership page reviewed through search-indexed publisher content; constituency not supplied. Partial leadership-only coverage, not a complete assembly roster.')
add('Gombe','Rt. Hon. Abubakar M. Luggerewo',None,'https://gombestate.gov.ng/pages/legislature.php','Gombe State Government','Speaker',note='Official legislature page supplies speaker only and no constituency. Partial leadership-only coverage; no seat inferred.')
add('Taraba','Rt Hon John Kizito Bonzena',None,'https://www.tarabastate.gov.ng/government','Taraba State Government','Speaker',note='Official government directory supplies speaker only and no constituency. Partial leadership-only coverage; no seat inferred.')
add('Kogi','Rt Hon Aliyu Umar Yusuf','Lokoja II','https://kogistate.gov.ng/profile/rt-honourable-aliyu-umar-yusuf/','Kogi State Government','Speaker',note='Official speaker profile identifies Lokoja II and the 8th Assembly. Partial leadership-only coverage. Promotional impact claims from biography are not imported as performance metrics.')
for state,name in [('Borno','Hon. Abdulkarim Lawan'),('Katsina','Rt Hon. Nasir Yahaya'),('Sokoto','Rt Hon. Tukur Bala')]:
 add(state,name,None,'https://www.cpahq.org/directory/'+state.lower()+'/','Commonwealth Parliamentary Association','Speaker',note='CPA branch leadership directory reviewed via indexed official publisher text on 4 November 2026. No row-level effective date or constituency supplied. Partial leadership-only coverage; not a complete assembly roster.')
add('Niger','Barrister Abdulmalik Sarkin Daji',None,'https://www.radionigeriakaduna.gov.ng/2026/10/01/nigeria-66-niger-speaker-congratulates-niger-people-nigerians/','Radio Nigeria Kaduna (FRCN)','Speaker',note='Dated public broadcaster report identifies speaker on 1 October 2026. Constituency is not supplied; no seat inferred. This is partial named-person coverage, not a complete roster.')
u='https://www.radionigeriakaduna.gov.ng/2026/10/13/kaduna-assembly-seeks-autonomy-for-multi-campus-nursing-college-midwifery/'
add('Kaduna','Ali Kalat','Jema’a',u,'Radio Nigeria Kaduna (FRCN)','Member',note='Dated public broadcaster report identifies the member and motion sponsor on 13 October 2026. Partial named-person coverage; no tenure date inferred.')
add('Kaduna','Henry Magaji Danjuma',None,u,'Radio Nigeria Kaduna (FRCN)','Deputy Speaker',note='Dated public broadcaster report identifies deputy speaker presiding on 13 October 2026. Constituency is not supplied; no seat inferred. Partial named-person coverage.')
u='https://nbs.na.gov.ng/2026/09/03/sule-urges-nigerian-youths-to-embrace-responsible-citizenship/'
add('Nasarawa','Dr. Danladi Jatau',None,u,'Nasarawa Broadcasting Service','Speaker',note='State broadcaster report published 4 September 2026 identifies speaker and deputy. Constituencies are not supplied; no seats inferred. Partial named-person coverage.')
add('Nasarawa','Mohammed Adamu Oyanki',None,u,'Nasarawa Broadcasting Service','Deputy Speaker',note='State broadcaster report published 4 September 2026 identifies the deputy speaker representing the speaker at the students’ parliamentary sitting. Constituency is not supplied; no seat inferred.')
add('Plateau','Rt Hon Naanlong Gapyil Daniel',None,'https://statehouse.gov.ng/plateau-leaders-commit-to-peace-at-interactive-session-with-president-tinubu-fg-approves-n2bn-for-victims/','State House, Abuja','Speaker',note='Presidency release published 29 April 2026 names the speaker among a Plateau delegation. Constituency is not supplied; no seat inferred. Partial named-person coverage.')
add('Zamfara',"Rt Hon Bilyaminu Ismail Moriki",'Zurmi West','https://molga.zamfara.gov.ng/speaker/','Zamfara Ministry of Local Government and Chieftaincy Affairs','Speaker',note='Official ministry speaker profile identifies the 7th Assembly and Zurmi West. No row-level update date supplied. Partial leadership-only coverage; party history is not imported.')
s=BeautifulSoup((P/'adamawa-planning-next.html').read_text(),'html.parser')
for c in s.select('.elementskit-info-image-box'):
 name=c.select_one('.elementskit-box-style-content');role=c.select_one('.elementskit-info-box-title')
 if not name or not role:continue
 name=' '.join(name.stripped_strings)
 if name=='Hon. Yohanna Sahabo Jauro':continue # same name tokens as deputy minority leader; one person, not two
 add('Adamawa',name,None,'https://adspc.ad.gov.ng/state-legislative-council/','Adamawa State Planning Commission',role.get_text(' ',strip=True),note='Updated official council directory includes Ganye successor Misa Musa and Mayo-Belwa successor Musa Mohammed Kallamu. Constituencies are not displayed and remain unverified. Reordered duplicate Sahabo Yohanna Jauro / Yohanna Sahabo Jauro merged into one entry; source has 25 cards but 24 distinct people. Older state-government roster with deceased/replaced occupants is excluded.')
assert sum(r['state']=='Adamawa' for r in rows)==24
u='https://www.theconclaveng.com/maikasuwa-dangoje-emerges-kebbi-assembly-speaker/amp/'
for name,seat,role in [('Alhaji Salihu Maikasuwa-Dangoje','Sakaba','Speaker'),('Alhaji Adamu Birnin-Yauri','Ngaski','Member'),('Alhaji Lawal Haruna','Fakai','Member')]:
 add('Kebbi',name,seat,u,'News Agency of Nigeria, republished by The Conclave',role,note='Dated NAN report of 3 June 2026 identifies the elected speaker and two named nominating members. Current speaker cross-checked against Premium Times 4 June 2026 and October NAN report. Old official state roster predates leadership changes and is not used. Partial named-person coverage.')
u='https://dailypost.ng/2026/10/20/appear-before-pac-with-financial-records-yobe-speaker-tells-queried-mdas-lgs/'
for name,role in [('Rt Hon Chiroma Buba Mashio','Speaker'),('Hon. Bulama Bukar','Public Accounts Committee chair')]:
 add('Yobe',name,None,u,'Daily Post Nigeria',role,note='Dated report on 20 October 2026 identifies the speaker and Public Accounts Committee chair. No constituencies supplied. CPA directory still lists former speaker Ahmed Lawan Mirwa and is excluded. Partial named-person coverage.')
add('Yobe','Rt. Hon. Ya’u Usman Dachia',None,'https://fmino.gov.ng/auda-nepad-and-yobe-state-government-launch-innovative-smallholder-farmers-support-and-youth-smart-irrigation-program/','Federal Ministry of Information and National Orientation / AUDA-NEPAD Nigeria','Deputy Speaker',note='Official release identifies deputy speaker launching the programme on 5 December 2025; dated evidence, not a live-certified current office register. Constituency not supplied.')
dates={'Niger':'2026-10-01','Kaduna':'2026-10-13','Nasarawa':'2026-09-04','Plateau':'2026-04-29','Kebbi':'2026-06-03','Yobe':'2026-10-20'}
for r in rows:
 if r['state'] in dates:r['source_date']=dates[r['state']];r['reference_year']=2026
 if r['name']=='Rt. Hon. Ya’u Usman Dachia':r['source_date']='2025-12-05';r['reference_year']=2025
for r in rows:
 if r['state']=='Zamfara':
  r['note']+=' Speaker role independently corroborated by Channels Television on 5 October 2026; report concerns an assembly dispute and is not treated as proof of allegations or performance.'
  r['corroborating_source_url']='https://www.channelstv.com/2026/10/05/defected-lawmakers-were-suspended-long-before-leaving-apc-zamfara-speaker/'
  r['corroboration_date']='2026-10-05'
 if not r.get('source_date'):r['note']+=' Directory snapshot reviewed 4 November 2026; no publisher effective date, so not a certified live office register.'
(P/'northern-officials-next.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))
print(len(rows))
