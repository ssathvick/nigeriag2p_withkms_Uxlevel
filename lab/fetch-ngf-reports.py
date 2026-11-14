import json,re,urllib.request,concurrent.futures
from pathlib import Path
root=Path('territory-data');data=json.loads((root/'public/data.json').read_text());raw=root/'raw'
def get(s):
 if s['id']=='NG37':return
 slug=s['name'].lower().replace(' ','-');url='https://www.publicfinance.ngf.org.ng/state-explorer/'+slug+'/'
 try:
  html=urllib.request.urlopen(url,timeout=45).read().decode();(raw/('ngf-'+slug+'.html')).write_text(html,encoding='utf-8')
  plain=re.sub('<[^>]+>',' ',html);plain=re.sub(r'\s+',' ',plain)
  found=re.search(r'GDP\s*\(2023\)\s*-?\s*(?:₦|&#8358;|&#x20a6;)\s*([\d,]+)\s*million',plain,re.I)
  return {'state_id':s['id'],'state_name':s['name'],'url':url,'gdp_ngn':int(found[1].replace(',',''))*1000000 if found else None,'excerpt':found[0] if found else plain[plain.find('GDP'):plain.find('GDP')+150]}
 except Exception as e:return {'state_name':s['name'],'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: rows=[r for r in pool.map(get,data['states']) if r]
(raw/'ngf-gdp-2023.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2))
