"""Reviewed manual source ledger. No fuzzy matching or live-roster scraping."""
import json,hashlib,requests,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw');base=json.loads((P/'northern-officials-next.json').read_text()); additions=[]; corrections=[]; activities=[];withdrawals=[]
def oid(state,name):return 'office-'+hashlib.sha256(('State House of Assembly|'+state+'|'+name).encode()).hexdigest()[:12]
def corr(state,name,seat,url,publisher,date=None,note='',year=None):
 assert len([x for x in base if x['state']==state and x['name']==name])==1,(state,name)
 corrections.append(dict(id=oid(state,name),state=state,name=name,constituency=seat,source_url=url,source_name=publisher,source_date=date,reference_year=year or (int(date[:4]) if date else None),note=note))
def add(state,name,seat,url,publisher,date,role='Member',note=''):
 assert not any(x['state']==state and x['name']==name for x in base+additions)
 additions.append(dict(state=state,name=name,constituency=seat,source_url=url,source_name=publisher,source_date=date,reference_year=int(date[:4]),role=role,chamber='State House of Assembly',note='Dated named-person report; partial coverage, not a certified live register. '+note))
def event(key,date,title,category,url,publisher,people,summary,attribution,qualification='Dated source report; not a full activity register or independent outcome audit.'):
 for state,name in people:assert any(x['state']==state and x['name']==name for x in base+additions),(state,name)
 activities.append(dict(id=key,date=date,date_basis='Source publication date; exact event date is not inferred.',reference_year=int(date[:4]),title=title,category=category,source_url=url,source_name=publisher,classification='published',level='state constituency / named legislative action',status='Reported legislative activity',qualification=qualification,summary=summary,attribution=attribution,member_ids=[oid(*p) for p in people]))
inec='https://wp1.inecnigeria.org/wp-content/uploads/2024/02/2023-GENERAL-ELECTION-REPORT-1.pdf'
for name,seat,match in [
 ('RT. Hon. Bathiya Wesley','Hong (Hong II)','Wesley Bathiya'),
 ('Hon Umar Suleiman Alkali','Yola North','Umar Suleiman Alkali'),
 ('Hon. Umar Bobbo Ismaila','Fufore/Gurin (Fufore I)','Umar Bobbo Ismaila'),
 ('Hon. Adum Hellapaburi John','Uba/Gaya (Hong I)','Adum Hyellapaburi John'),
 ('Hon. Yerima Moses','Michika','Yerima Moses'),
 ('Hon. Kabiru Minjinyawa','Yola South','Minjinyawa Kabiru')]:
 corr('Adamawa',name,seat,inec,'INEC — Report of the 2023 General Election',year=2023,note=f'Historical 2023 elected-results seat mapping, reviewed against the current Planning Commission named-member directory. Explicit manual match to INEC name {match}; not a fresh 2026 election result. Indexed primary table reviewed; direct report download unavailable. Current-directory provenance remains separate.')
u='https://thenationonlineng.net/just-in-six-adamawa-assembly-members-dump-pdp/'
for name,seat,match in [('Hon. Buba Mohammed Jijiwa','Jada/Mbulo','Mohammed Buba Jidjiwa, deputy speaker'),('Hon. Calvin Kefas','Toungo','Kefas Kalvin'),('Hon. Geoffrey Bulus','Leko/Koma','Bulus Geoffrey'),('Hon. Haruna J. Jilantikiri','Madagali','Haruna Jilantikiri'),('Hon. Kefas Emmanuel','Song','Kefas Emmanuel'),('Hon. Jingi Belel Ahmed','Maiha','Ahmed Jingi Bele')]:
 corr('Adamawa',name,seat,u,'The Nation','2026-02-24',note=f'Explicit manual identity/seat comparison: source identifies {match}. Political resignation is from party, not assembly; party affiliation is not imported.')
u='https://thegraphicnews.ng/adamawa-speaker-14-legislators-withdraws-membership-from-pdp/'
for name,seat,match in [('Hon. Mamuno Raymond Kate','Demsa','Kate Raymond Mamuno'),('Hon. Japheth Hammanjabu','Verre','Japhet Hammanjabu'),('Hon. Bauna P. Myandasa','Lamurde','Bauna Myandiasa')]:
 corr('Adamawa',name,seat,u,'The Graphic Newspaper','2026-02-28',note=f'Manual comparison of current directory identity with reported member {match}. Only seat attribution imported, not party status.')
u='https://thesun.ng/6-adamawa-lawmakers-dump-pdp-fintiri-to-follow-soon/'
corr('Adamawa','Hon. Bulus Kantomon Napthali','Shelleng',u,'The Sun','2026-02-26',note='Manual match to Bulus Kantomon Naphtali; same three name tokens with transposed spelling in third token. INEC 2023 elected-results table independently gives exact directory name and Shelleng.')
u='https://guardian.ng/news/adamawa-assembly-summons-council-chairmen-for-performance-review/'
for name,seat,match in [('Hon. Mackondo Pwamwakeno M.','Numan','Pwamwakeno Mackondo'),('Hon. Sahabo Yohanna Jauro','Mubi South','Sahabo Yohanna Jauro')]:
 corr('Adamawa',name,seat,u,'The Guardian Nigeria','2025-07-31',note=f'Explicit dated member/seat identification; manual match to {match}. 2025 seat evidence retained separately from later directory membership snapshot.')
event('adamawa-council-oversight-motion-20250731','2025-07-31','Motion seeking council-chairmen performance and financial records','Oversight',u,'The Guardian Nigeria',[('Adamawa','Hon. Mackondo Pwamwakeno M.')],'Reported sponsorship of a motion requiring council chairmen to present performance and financial records. No completed investigation, recovery or accountability outcome is inferred.','Source explicitly attributes motion to Pwamwakeno Mackondo of Numan; name manually matched to existing directory entry.')
event('adamawa-council-oversight-support-20250731','2025-07-31','Supported council-chairmen oversight motion','Debate contributions',u,'The Guardian Nigeria',[('Adamawa','Hon. Sahabo Yohanna Jauro')],'Reported contribution supporting a council performance review. No sponsorship credit, full attendance rate or completed audit is claimed.','Source explicitly names Sahabo Yohanna Jauro as supporting the motion.')
u='https://insightnortheastng.net/adamawa-assembly-adopts-5-point-resolutions-over-yola-mau-girei-road-crashes/'
corr('Adamawa','Hon. Babangida Mohammed Jidda','Nasarawo-Binyeri',u,'Insight Northeast Nigeria','2026-09-08',note='Manual match to report name Muhammed Babangida Njidda; INEC 2023 elected table separately identifies Njidda B. Mohammed for this seat. Regional report date retained, no vote totals or outcomes imported.')
u='https://von.gov.ng/apcs-misa-musa-wins-ganye-constituency-by-election-in-adamawa/'
corr('Adamawa','Hon. Misa Musa','Ganye',u,'Voice of Nigeria','2025-08-17',note='2025 by-election winner/seat explicitly named by public broadcaster; later current Planning Commission directory independently confirms named membership. No old deceased occupant carried forward.')
u='https://punchng.com/adamawa-lawmaker-resigns-from-pdp/'
add('Adamawa','Alhaji Abubakar Abdullahi','Girei',u,'The Punch','2026-02-24',note='Explicitly identified as assembly member during plenary. Resignation concerned party membership, not legislative office; no party affiliation imported.')
u='https://nilds.com/nilds-hosts-adamawa-state-house-of-assembly/'
event('adamawa-nilds-training-20260824','2026-08-24','Participated in NILDS legislative capacity-building programme','Capacity building',u,'National Institute for Legislative and Democratic Studies',[('Adamawa','RT. Hon. Bathiya Wesley'),('Adamawa','Hon. Mamuno Raymond Kate')],'NILDS names the speaker and majority leader among participants in a legislative training programme. Training attendance does not establish improved performance.','Institution explicitly names Bathiya Wesley and Kate Mamuno Raymond; manually matched reversed name order for existing majority-leader entry.','Training institution self-report of participation, not an independent competency or impact assessment.')
u='https://dailypost.ng/2026/09/08/yobe-assembly-approves-second-reading-of-biomedical-engineering-institute-bill/'
corr('Yobe','Hon. Bulama Bukar','Gujba',u,'Daily Post Nigeria','2026-09-08',note='Article explicitly orders four named constituencies and corresponding four members; Gujba maps to first named member Bulama Bukar.')
for name,seat in [('Mohammed Isa Bello','Mamudo'),('Sanda Kara Bade','Bade West'),('Musa Lawan Majakura','Nguru II'),('Hon. Nasiru Hassan Yusuf',None)]:add('Yobe',name,seat,u,'Daily Post Nigeria','2026-09-08',role='Majority leader' if seat is None else 'Member',note='Named participant in legislative debate; no inferred seat for majority leader.')
event('yobe-biomedical-debate-leader-20260908','2026-09-08','Led debate on proposed biomedical institute','Debate contributions',u,'Daily Post Nigeria',[('Yobe','Hon. Nasiru Hassan Yusuf')],'Reported lead contribution on an executive bill at second reading. Not credited as bill sponsor, enacted law or completed institute.','Report explicitly identifies majority leader as leading debate.')
event('yobe-biomedical-debate-members-20260908','2026-09-08','Contributed to biomedical-institute debate','Debate contributions',u,'Daily Post Nigeria',[('Yobe','Hon. Bulama Bukar'),('Yobe','Mohammed Isa Bello'),('Yobe','Sanda Kara Bade'),('Yobe','Musa Lawan Majakura')],'Report names four members contributing to the second-reading discussion. No individual division vote, sponsorship, enactment or project delivery is inferred.','Four participants and seats explicitly listed by reporter; shared event with individual participation.')
u='https://www.radionigeriakaduna.gov.ng/2026/04/14/niger-assembly-regulates-scavengers-scrap-dealers/'
add('Niger','Mohammed Garba','Agwara',u,'Radio Nigeria Kaduna (FRCN)','2026-04-14',note='Joint committee chairman explicitly named with constituency.')
event('niger-scrap-committee-report-20260414','2026-04-14','Presented joint-committee report on scrap-dealer regulation','Committee work',u,'Radio Nigeria Kaduna (FRCN)',[('Niger','Mohammed Garba')],'Reported presentation of committee findings after stakeholder hearing. No personal bill-sponsor credit or safety outcome is assigned.','Broadcaster explicitly identifies report presenter Mohammed Garba of Agwara.')
corr('Niger','Barrister Abdulmalik Sarkin Daji','Mariga','https://thesun.ng/niger-bago-hails-speaker-sarkindaji-at-44-lauds-assembly-leadership/','The Sun','2026-01-07',note='Report of governor’s dated statement explicitly identifies speaker and Mariga constituency. Praise is not imported as performance evidence.')
u='https://www.radionigeriakaduna.gov.ng/2025/09/11/speaker-liman-flags-off-%E2%82%A610-million-community-development-projects/'
add('Kaduna','Rt. Hon. Yusuf Dahiru Liman','Makera',u,'Radio Nigeria Kaduna (FRCN)','2025-09-11','Speaker','Public broadcaster identifies speaker and constituency. Evidence is dated 2025, not an inferred currentness guarantee.')
corr('Kaduna','Henry Magaji Danjuma','Kagarko','https://www.radionigeriakaduna.gov.ng/2023/06/13/kdha-elects-speaker-deputy/','Radio Nigeria Kaduna (FRCN)','2023-06-13',note='Historical seat identification at 2023 inauguration, paired with existing 13 October 2026 named-deputy-speaker report. Same exact name; 2023 seat mapping remains dated, not relabelled 2026.')
u='https://von.gov.ng/sokoto-assembly-adopts-state-police-amendment-bill/'
add('Sokoto','Mustapha Abdullahi','Sokoto South II',u,'Voice of Nigeria','2026-10-31','Deputy majority leader')
event('sokoto-state-police-motion-20261031','2026-10-31','Moved motion on state-police constitutional amendment','Motions',u,'Voice of Nigeria',[('Sokoto','Mustapha Abdullahi')],'Reported presentation and motion for Assembly approval of the constitutional proposal. Not evidence of final national enactment or functioning state police.','Public broadcaster explicitly attributes motion to deputy majority leader of Sokoto South II.')
u='https://von.gov.ng/nasarawa-assembly-confirms-8-commissioner-nominees/'
for name,seat,role in [('Suleiman Yakubu Azara',None,'Majority leader'),('Luka Iliya Zhekaba',None,'Minority leader'),('Dr Ibrahim Peter Akwe','Obi One','Member'),('Esson Mairiga',None,'Member')]:add('Nasarawa',name,seat,u,'Voice of Nigeria','2026-08-20',role,'Unstated constituencies remain null.')
event('nasarawa-animal-health-bill-20260820','2026-08-20','Sponsored proposed animal-health college bill','Bills',u,'Voice of Nigeria',[('Nasarawa','Dr Ibrahim Peter Akwe')],'Report identifies sponsor of a proposed College of Animal Health and Production Technology bill at first reading. Does not establish enactment, a functioning college or service improvements.','Bill sponsorship expressly attributed to Dr Ibrahim Peter Akwe of Obi One.')
event('nasarawa-nominee-confirmation-motion-20260820','2026-08-20','Moved and seconded commissioner-confirmation motion','Motions',u,'Voice of Nigeria',[('Nasarawa','Suleiman Yakubu Azara'),('Nasarawa','Luka Iliya Zhekaba')],'Majority leader moved and minority leader seconded confirmation motion after screening. No individual vote record or nominee performance is inferred.','Article names mover and seconder separately; shared event preserves both roles.')
u='https://von.gov.ng/legislator-nawoj-partner-to-boost-womens-political-participation/'
add('Nasarawa','Hon. Hajarat Danyaro Ibrahim','Nasarawa Central',u,'Voice of Nigeria','2026-03-12',note='Named member and Women Affairs Committee chair in report of NAWOJ meeting.')
event('nasarawa-nawoj-engagement-20260312','2026-03-12','Met NAWOJ leadership on women’s political participation','Citizen engagement',u,'Voice of Nigeria',[('Nasarawa','Hon. Hajarat Danyaro Ibrahim')],'Reported meeting and proposed collaboration on women’s participation. No mobilisation reach or improved representation outcome is claimed.','Report explicitly identifies lawmaker receiving NAWOJ leadership.')
u='https://thenationonlineng.net/nasarawa-speaker-jatau-loses-ticket-to-colleague/'
corr('Nasarawa','Dr. Danladi Jatau','Kokona West',u,'The Nation','2026-05-18',note='Report explicitly identifies existing speaker’s state seat. Election discussed is a future federal candidacy; not a change of current office.')
add('Nasarawa','Hon. Daniel Ogah Ogazi','Kokona East',u,'The Nation','2026-05-18',note='Explicitly described as sitting colleague in state assembly; future federal primary result is not treated as holding federal office.')
u='https://triumphnewspapers.ng/plateau-assembly-passes-pension-board-bill-for-second-reading/'
for name,seat,role in [('Hon. Joseph Gokum',None,'Majority leader'),('Rt. Hon. Madaki Isa Ajiji',None,'Deputy Speaker'),('Hon. Abel Nansak','Langtang North North','Member'),('Hon. Daniel Nanbol Listick',None,'Member')]:add('Plateau',name,seat,u,'Triumph Newspapers','2026-07-09',role,'Report identifies named plenary participants; unreported seats remain null.')
event('plateau-pension-bill-motion-20260709','2026-07-09','Moved and seconded pension-board bill consideration','Motions',u,'Triumph Newspapers',[('Plateau','Hon. Joseph Gokum'),('Plateau','Rt. Hon. Madaki Isa Ajiji')],'Report identifies majority leader moving and deputy speaker seconding bill consideration at second reading. No enactment or pensions paid is claimed.','Mover and seconder expressly named; not treated as original bill sponsors.')
u='https://www.channelstv.com/2023/06/26/chiroma-mashio-emerges-speaker-of-yobe-8th-assembly/'
for name,seat in [('Rt Hon Chiroma Buba Mashio','Jajere'),('Rt. Hon. Ya’u Usman Dachia','Jakusko')]:
 corr('Yobe',name,seat,u,'Channels Television','2023-06-26',note='Historical inauguration seat attribution, manually matched to current dated named-person evidence already in atlas. Seat evidence remains dated 2023; no tenure continuity inferred solely from old inauguration.')
u='https://www.thecable.ng/katsina-sokoto-assemblies-elect-apcs-nasir-yahya-tukur-bala-as-speakers/'
for state,name,seat in [('Katsina','Rt Hon. Nasir Yahaya','Daura'),('Sokoto','Rt Hon. Tukur Bala','Bodinga South')]:
 corr(state,name,seat,u,'News Agency of Nigeria, reported by TheCable','2023-06-13',note='Historical inauguration seat mapping, paired with later CPA directory and 2026 leadership corroboration. Not presented as a 2026 election result.')
u='https://punchng.com/new-kano-lawmaker-pledges-not-to-be-bench-warmer/'
add('Kano','Yusuf Datti-Hussaini','Dawakin Kudu',u,'News Agency of Nigeria, republished by The Punch','2026-09-29',note='NAN explicitly reports swearing-in after September2026 by-election. Replaces stale directory occupant Rabiu Shuaibu; predecessor activities must remain linked to predecessor.')
withdrawals.append(dict(id=oid('Kano','Hon. Rabiu Shuaibu'),reason='Former Dawakin Kudu state member moved to House of Representatives; successor Yusuf Datti-Hussaini sworn in 29 September 2026. Archive former state-office record; preserve historical March2026 activity and do not transfer it to successor.',source_url='https://tribuneonlineng.com/apc-wins-kano-assembly-bye-election-by-22620-votes/',source_name='Nigerian Tribune',source_date='2026-09-20',corroborating_source_url=u))
for key,data in [('additions',additions),('corrections',corrections),('activity',activities),('withdrawals',withdrawals)]:
 assert len({x.get('id',oid(x.get('state',''),x.get('name',''))) for x in data})==len(data)
 (P/f'northern-round3-{key}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print({k:len(v) for k,v in [('additions',additions),('corrections',corrections),('activity',activities),('withdrawals',withdrawals)]})
if __name__=='__main__':
 urls={x['source_url'] for x in additions+corrections+activities+withdrawals if not x['source_url'].endswith('.pdf')}
 def cache(u):
  k='northern-round3-'+hashlib.sha256(u.encode()).hexdigest()[:12]
  try:
   r=requests.get(u,timeout=25);r.raise_for_status();(P/(k+'.html')).write_text(r.text);(P/(k+'.txt')).write_text(BeautifulSoup(r.text,'html.parser').get_text(' ',strip=True));return dict(url=u,file=k+'.html',status=r.status_code)
  except Exception as e:return dict(url=u,error=str(e))
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:logs=list(pool.map(cache,sorted(urls)))
 (P/'northern-round3-cache-log.json').write_text(json.dumps(logs,indent=2));print('cached',sum('file' in x for x in logs),'of',len(logs))
