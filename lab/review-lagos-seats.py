import json,hashlib,requests
from pathlib import Path
p=Path('territory-data/raw');rows=json.loads((p/'lagos-officials-next.json').read_text())
# Current official directory identities checked against its 10th Assembly PDF.
# Explicit reviewed name tokens, never source order or fuzzy matching.
seats={'OBASA':'Agege I','MERANDA':'Apapa I','ADAMS':'Eti-Osa I','MOJEED':'Ibeju Lekki I','KASUNMU':'Ikeja II','DAVID':'Badagry II','ADEWALE':'Ifako Ijaiye I','SANNI':'Kosofe I','AYODEJI':'Agege II','OLUMOH':'Ajeromi Ifelodun I','AKANBI':'Ajeromi Ifelodun II','OLATUNJI':'Alimosho I','JOSEPH':'Alimosho II','STELLA':'Amuwo Odofin I','RAUF':'Amuwo Odofin II','ROTIMI':'Surulere II','MUSIBAU':'Apapa II','SAANU':'Badagry I','TOBUN':'Epe I','OGUNKELU':'Epe II','YISHAWU':'Eti-Osa II','OLUWADAMILARE':'Ibeju Lekki II','EMMANUEL':'Ifako Ijaiye II','ADESEYI':'Ikeja I','ADETOKUNBO':'Ikorodu I','ABIODUN':'Ikorodu II','SAHEED':'Kosofe II','OLUMEGBON':'Lagos Island I','AFINNI':'Lagos Island II','OWOLABI':'Lagos Mainland I','ADEKOLA':'Lagos Mainland II','AKINSANYA':'Mushin I','MUYIDEEN':'Mushin II','ADEBISI':'Ojo I','TIJANI':'Ojo II','OLUKAYODE':'Oshodi Isolo I','OLAYINKA':'Oshodi Isolo II','ABIMBOLA':'Somolu I','OLU':'Somolu II','ELLIOT':'Surulere I'}
pdf='https://lagoshouseofassembly.gov.ng/home/wp-content/uploads/2024/05/10-Assembly.pdf'
resp=requests.get(pdf,timeout=30);resp.raise_for_status();(p/'lagos-10th-assembly.pdf').write_bytes(resp.content)
for r in rows:
 # OLAYINKA also occurs in Muyideen's name; narrower reviewed identity takes precedence.
 keys=[k for k in seats if k in r['name'].replace('.',' ').split()]
 if 'MUYIDEEN' in keys:keys=['MUYIDEEN']
 assert len(keys)==1,(r['name'],keys)
 r['constituency']=seats[keys[0]]
 r['secondary_source_url']=pdf
 r['note']+=' Constituency cross-checked against the official 2023–2027 roster PDF (2024 upload); name abbreviations manually reviewed. PDF Agege II spelling “Agage” normalized. Historical PDF leadership titles and parties are not imported.'
(p/'lagos-officials-next.json').write_text(json.dumps(rows,indent=2))
def repid(key):
 r=next(r for r in rows if key in r['name']);return 'office-'+hashlib.sha256((r['chamber']+'|'+r['state']+'|'+r['name']).encode()).hexdigest()[:12]
events=[]
def event(key,date,title,slug,person,summary,category):
 events.append(dict(id=key,date=date,date_basis='Publisher report date; event timing described in the report',reference_year=int(date[:4]),title=title,category=category,source_url='https://lagoshouseofassembly.gov.ng/home/'+slug+'/',source_name='Lagos State House of Assembly',classification='published',level='state assembly / named committee participant',status='Officially reported activity',qualification='Official self-report; not an independent outcome audit, complete tenure total or evidence of project delivery.',summary=summary,attribution='Named committee chair in report manually matched to current official member profile and 10th Assembly roster; expanded name variants reviewed.',member_ids=[repid(person)]))
event('lagos-land-review-20260609','2026-06-09','Land-petition committee report presented','lagos-assembly-adopts-commt-recommendations-on-igbaro-oteshade-royal-family-land-excision','AJOMALE','Oladipupo Ajomale presented the committee report following a reported site visit. The House adopted recommendations; implementation and resolution of the dispute are not established.','Oversight')
event('lagos-wealth-review-20260604','2026-06-04','Wealth Fund Bill committee report presented','lagos-assembly-adopts-commt-recommendations-on-wealth-fund-bill-2025','SAHEED','Obafemi Saheed presented the Finance Committee report on the Wealth Fund Bill. Recommendations were adopted as amended; this is not proof of assent, fund establishment or investment returns.','Legislative review')
(p/'lagos-activity-next.json').write_text(json.dumps(events,indent=2))
print('Reviewed',len(rows),'Lagos members and',len(events),'activity records')
