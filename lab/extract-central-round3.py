import json,hashlib
from pathlib import Path
P=Path('territory-data/raw');d=json.loads(Path('territory-data/public/data.json').read_text());members=d['representatives']['members'];additions=[];corrections=[];events=[]
def existing(state,key):
 matches=[r for r in members if r['chamber']=='State House of Assembly' and r['state_name']==state and key.lower() in r['name'].lower()];assert len(matches)==1,(state,key);return matches[0]['id']
def correct(state,key,seat,url,pub,date=None,note=''):
 corrections.append(dict(id=existing(state,key),constituency=seat,source_url=url,source_name=pub,source_date=date,note=note))
imo='https://imha.imostate.gov.ng/inauguration-of-the-assembly/'
for key,seat in [('CHIKE OLEMGBE','Ihitte Uboma'),('AMARA IWUANYANWU','Nwangele'),('Kanayo Onyemaechi','Owerri West'),('Chigozie Nwaneri','Oru East'),('OSUJI SAMUEL','Isiala Mbano'),('OFURUM KELECHI','Owerri North')]:
 correct('Imo',key,seat,imo,'Imo State House of Assembly',note='Seat supplied in the official 10th Assembly leadership section and matched to the existing current directory identity. The separate 9th Assembly section is not used. No publication/effective date is supplied.')
rv='https://hoa.rv.gov.ng/members.html';tvc='https://www.tvcnews.tv/17-rivers-house-of-assembly-members-defect-to-apc/'
for key,seat in [('Martin Chike','Obio Akpor I'),('Dumle','Gokana'),('Linda','Okrika'),('Nwabochi','Ogba Egbema Ndoni I')]:
 correct('Rivers',key,seat,rv,'Rivers State House of Assembly',note='Official member-card seat matched to the existing government-directory identity; shortened name variants manually reviewed. Directory has no effective date. TVC membership report of 5 December 2025 independently corroborates the named person and area, but omits the division for the chief whip.')
def add(name,seat,url,pub,date,note,secondary=None):
 r=dict(state='Rivers',name=name,constituency=seat,source_url=url,source_name=pub,role='Member',source_date=date,reference_year=int(date[:4]),note=note,chamber='State House of Assembly')
 if secondary:r['secondary_source_url']=secondary
 additions.append(r)
for name,seat in [('Hon. Solomon Wami','Port Harcourt I'),('Hon. Lemchi Nyeche','Ikwerre'),('Hon. Bernard Ngbar','Tai'),('Hon. Davids Arnold','Ogu Bolo'),('Hon. Smart Adoki','Port Harcourt II'),('Hon. Azeru Opara','Port Harcourt III'),('Hon. Barile Nwakor','Khana I'),('Hon. Sylvanus Nwankwo','Omuma'),('Hon. Emilia Lucky-Amadi','Obio Akpor II'),('Hon. Nkemjika Ezekwe','Ogba Egbema Ndoni II'),('Hon. Gerald Oforji','Oyigbo')]:
 add(name,seat,tvc,'TVC News','2025-12-05','Named serving member in dated broadcaster roster. Constituency division checked against the official assembly member card where present. Shortened/reordered names manually reviewed. Party changes and future candidacy are not imported; this is not a certified live register.',None if 'Gerald' in name else rv)
url='https://leadership.ng/rivers-assembly-inaugurates-newly-elected-lawmakers/'
for name,seat in [('Hon. Napoleon Ukalikpe','Ahoada East II'),('Hon. Henrietta Dinebari Loolo','Khana II')]:
 add(name,seat,url,'Leadership','2026-03-05','Report confirms swearing-in after the February 2026 by-elections. Published timestamp verified in article metadata; election victory alone was not used as proof of inauguration.')
url='https://www.premiumtimesng.com/news/headlines/918369-rivers-assembly-reinstates-three-pro-fubara-lawmakers.html'
for name,seat in [('Hon. Timothy Oruibienimigha','Opobo Nkoro'),('Hon. Victor Jumbo','Bonny'),('Hon. Sokari Goodboy Sokari','Ahoada West')]:
 add(name,seat,url,'Premium Times','2026-10-19','Report of reinstatement during the 68th sitting, citing the Speaker’s media aide. Earlier vacancy/suspension accounts are not treated as current status. Personal attendance or performance is not inferred from reinstatement.')
rn='https://radionigeriaibadan.gov.ng/'
for key,seat in [('Ogundoyin','Ibarapa East'),('Fadeyi','Ona Ara')]:
 correct('Oyo',key,seat,rn+'2023/06/14/ogundoyin-speaker-of-oyo-assembly-for-second-time/','Radio Nigeria Ibadan (FRCN)','2023-06-14','10th Assembly inauguration report supplies the constituency; identity remains corroborated by the current state-government directory. Historical seat evidence is kept separate from the directory check date.')
for key,seat in [('Babalola Olasunkanmi','Egbeda'),('Salami Waliu','Irepo Olorunsogo'),('Oyekola Gbenga','Atiba')]:
 correct('Oyo',key,seat,rn+'2023/06/20/new-principal-officers-take-charge-at-oyha/','Radio Nigeria Ibadan (FRCN)','2023-06-20','10th Assembly officers report supplies seat; current government directory corroborates identity. Radio Nigeria places Salami in Irepo/Olorunsogo; a separate newspaper’s Oorelope label conflicts and is not adopted.')
correct('Oyo','Onaolapo Sanjo','Ogbomoso South','https://thenationonlineng.net/oyo-assembly-appoints-principal-officers/','The Nation','2023-06-21','Contemporaneous 10th Assembly leadership report supplies this seat; current government directory corroborates identity. Other inconsistent constituency labels in that report are not adopted.')
school='https://pmparrotng.com/2026/06/19/from-promise-to-fulfillment-hon-yusuf-adebisi-inspects-site-for-first-secondary-school-in-his-constituency/'
correct('Oyo','Adebisi Yusuf','Ibadan South West I',school,'PM Parrot','2026-06-19','Dated report explicitly identifies Ibadan South-West I. This resolves the missing division; a contradictory South-East I label in a separate 2023 newspaper report is not adopted.')
def event(key,state,people,date,title,category,url,pub,summary,note=''):
 events.append(dict(id=key,member_ids=[existing(state,k) for k in people],date=date,reference_year=int(date[:4]),title=title,category=category,source_url=url,source_name=pub,classification='published',level='state constituency / named legislative activity',status='Reported activity',qualification='Attributed published report; not an independent outcome audit or complete tenure total. '+note,summary=summary,attribution='Named person and role/constituency manually matched to the existing official directory; no fuzzy automatic attribution.',date_basis='Publication date; exact event date is not inferred.'))
event('oyo-teachers-motion-20231129','Oyo',['Oyekola Gbenga'],'2023-11-29','Motion on teachers’ retirement-age rules','Motions',rn+'2023/11/29/lawmaker-calls-for-implementation-of-teachers-retirement-age/','Radio Nigeria Ibadan (FRCN)','Reported sponsorship of a motion seeking adoption of revised teacher retirement rules. No implementation or pension outcome is established.')
event('oyo-budget-defence-20231213','Oyo',['Babalola Olasunkanmi','Oyekola Gbenga'],'2023-12-13','Committee participation in MDA budget defence','Oversight',rn+'2023/12/13/lawmakers-embark-on-budget-defence-for-oyo-mdas/','Radio Nigeria Ibadan (FRCN)','Named committee chair and vice-chair addressed the budget-defence exercise. No agency count, financial outcome or attendance rate is attributed.','Source mixes budget years and gives an inconsistent commencement weekday/date; these are excluded, and the publication date is retained.')
event('oyo-school-visit-20260619','Oyo',['Adebisi Yusuf'],'2026-06-19','Inspection of school construction site','Oversight',school,'PM Parrot','Reported site inspection of ongoing school construction. Expected opening and education benefits remain prospective; no independently verified completion is claimed.')
url='https://statesmannewspaper.com/imo-assembly-okays-motion-to-rehabilitate-emekuku-emii-ulakwo-road/'
event('imo-owerri-road-motion-20240614','Imo',['OFURUM KELECHI'],'2024-06-14','Motion requesting Owerri North road rehabilitation','Motions',url,'The Statesman','Named sponsor requested rehabilitation of Emekuku, Emii and Ulakwo roads. The reported resolution does not establish works completion.')
event('imo-ngor-road-motion-20240614','Imo',['OBINNA AMBROSE EGU'],'2024-06-14','Motion requesting Ngor Okpala road repairs','Motions',url,'The Statesman','Named sponsor requested palliative repairs on the Ihitte/Umukabia/Umuneke road. No procurement or completed repair is established.')
assert len(additions)==16 and len(corrections)==17
for kind,value in [('additions',additions),('corrections',corrections),('activity',events)]:
 (P/('central-round3-'+kind+'.json')).write_text(json.dumps(value,indent=2,ensure_ascii=False))
print('central round3',len(additions),len(corrections),len(events))
