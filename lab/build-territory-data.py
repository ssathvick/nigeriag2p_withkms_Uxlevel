"""Reproducible public aggregate build. Never exports beneficiary rows or locations."""
from pathlib import Path
import json,re,html,hashlib,datetime,sqlite3,collections,csv
import requests,numpy as np,rasterio
from rasterio.features import rasterize
ROOT=Path(__file__).parent; RAW=ROOT/'territory-data/raw'; OUT=ROOT/'territory-data/public';OUT.mkdir(parents=True,exist_ok=True)
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
def norm(s):return re.sub('[^a-z]','',s.lower()).replace('nassarawa','nasarawa').replace('abuja','').replace('federalcapitalterritory','fct')
catalogue=json.loads((ROOT/'nigeria-geography.json').read_text())
states=[{'id':a['id'],'name':a['name'],'level':'state','zone':a['zone_name'],'metrics':{}} for a in catalogue['areas'] if a['level']=='state']
byname={norm(s['name']):s for s in states};byid={s['id']:s for s in states}
sources={
 'mpi':{'name':'NBS Nigeria Multidimensional Poverty Index','year':2022,'url':'https://www.nigerianstat.gov.ng/download/1241254','classification':'published','note':'Tables D6 and D7, printed pages 100–104. Fieldwork 2021–2022. Survey estimates, not a current census. Borno results are not representative. Confidence intervals retained.','license':'NBS publication; extracted statistical facts with attribution'},
 'codes':{'name':'NBS MPI survey district codebook','year':2022,'url':'https://microdata.nigerianstat.gov.ng/index.php/catalog/71/variable/V7','classification':'published','note':'Official NBS survey identifiers (a1b), not INEC delimitation codes. District-to-state association checked against state names and NBS state-code prefix.','license':'NBS published codebook'},
 'lga':{'name':'GRID3 operational LGA boundaries','year':2021,'url':'https://www.arcgis.com/home/item.html?id=2bb616a49ee84f409427cc2143787113','classification':'published','note':'774 operational LGA polygons. March 2021 release; not certified electoral boundaries. Geometry simplified to 0.002 degrees for this display and raster aggregation.','license':'CC BY 4.0'},
 'states':{'name':'geoBoundaries / GRID3 state boundaries','year':2022,'url':'https://www.geoboundaries.org/api/current/gbOpen/NGA/ADM1/','classification':'published','note':'Pinned existing local NGA-ADM1-27671186, commit 9469f09. 37 explicit state-name mappings. Map does not show electoral boundaries.','license':'CC BY 4.0'},
 'population':{'name':'WorldPop 2020 UN-adjusted population','year':2020,'url':'https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/NGA/','classification':'modelled','note':'Approximate 1 km raster population summed by GRID3 LGA using pixel-centre assignment. Rounded estimates; boundary mismatch leaves some raster population unassigned. State estimates sum assigned LGAs. Not census counts or 2026 forecasts.','license':'CC BY 4.0'},
 'health':{'name':'GRID3 health facilities v4.0','year':2026,'url':'https://www.arcgis.com/home/item.html?id=9df52e12d0b5422f8f73c44d0dc91f8b','classification':'published','note':'Counts of listed facilities, not verified functioning facilities. October 2026 release. Non-exhaustive and not fully government-validated. State/LGA name matching only; unmatched records disclosed.','license':'CC BY 4.0'},
 'projects':{'name':'BudgIT / Tracka 2023 FG projects analysis','year':2023,'url':'https://budgit.org/wp-content/uploads/2023/06/FG-2023-Project-.pdf','classification':'published','note':'Printed page 10: state-attributed ZIP allocations and project counts. Rounded allocated budgets, not releases, payments or completed projects. Some projects are not attributable to a state. Project example on printed page 2 is illustrative coverage only.','license':'Published budget facts extracted with attribution; report remains with publisher'},
 'programme':{'name':'Nigeria G2P sandbox aggregate snapshot','year':2026,'url':'https://g2p.wverve.in/','classification':'synthetic','note':'Allowlisted aggregate counts from this demonstration installation only. Not Nigerian national programme coverage, eligibility, payment or settlement evidence. No personal records published.','license':'Local demonstration aggregates'},
 'simulation':{'name':'User-controlled planning scenario','year':2026,'url':'#simulation','classification':'synthetic','note':'Illustrative budget × assumed multiplier. Neither an economic forecast nor a causal impact estimate. Never added to published figures.','license':'Demonstration only'}
}
def measure(value,source,level,**kw):return {'value':value,'source':source,'year':sources[source]['year'],'level':level,'classification':sources[source]['classification'],**kw}
text=(RAW/'mpi.txt').read_text()
def table(start,end):
 block=text[text.index(start):text.index(end,text.index(start)+len(start))];lines=block.splitlines();result=[]
 for i,line in enumerate(lines):
  match=re.search(r'\b0\.\d{3}\b',line)
  if not match:continue
  values=re.findall(r'\d[\d,]*(?:\.\d+)?',line[match.start():])
  if len(values)!=11:continue
  name=line[:match.start()].strip()
  if not name:name=lines[i-1].strip()
  if i+1<len(lines) and lines[i+1].strip() in ['Central','North','South','East','West','North East','North West','South East','South West','Ibom','River','Abuja']:name+=' '+lines[i+1].strip()
  nums=[float(v.replace(',','')) for v in values]
  assert abs(nums[0]-nums[3]*nums[6]/10000)<.002,(name,nums)
  assert nums[4]<=nums[3]<=nums[5]
  result.append((name,nums))
 return result
state_rows=table('D6. Multidimensional poverty by State','D7. Multidimensional poverty')
district_rows=table('D7. Multidimensional poverty by senatorial district','D8.')
dedup={}
for name,values in district_rows:
 if name in dedup:assert dedup[name]==values,('Conflicting duplicate',name)
 dedup[name]=values
district_rows=list(dedup.items())
sources['mpi']['note']+=' The source repeats Osun West identically in D7; retained once after all 11 values matched.'
assert len(state_rows)==37,len(state_rows);assert len(district_rows)==109,len(district_rows)
def poverty_metrics(n,level):return {'poverty':measure(n[3],'mpi',level,unit='%',ci=[n[4],n[5]]),'mpi':measure(n[0],'mpi',level,unit='index',ci=[n[1],n[2]]),'poor_people':measure(round(n[10]*(1000000 if level=='state' else 1000)),'mpi',level,unit='people')}
for name,n in state_rows:
 s=byname[norm(name)];s['metrics'].update(poverty_metrics(n,'state'));s['caveat']='Survey result is not representative for Borno.' if s['name']=='Borno' else ''
codefile=RAW/'district-codebook.html'
if not codefile.exists():r=requests.get(sources['codes']['url'],timeout=40);r.raise_for_status();codefile.write_text(r.text)
codes={}
for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',codefile.read_text(),re.S):
 cells=[html.unescape(re.sub('<[^>]+>','',x)).strip() for x in re.findall(r'<td\b[^>]*>(.*?)</td>',tr,re.S)]
 if len(cells)>=2 and cells[0].isdigit():codes[norm(cells[1])]=int(cells[0])
assert len(codes)==109,len(codes)
districts=[];crosswalk=[]
for name,n in district_rows:
 code=codes[norm(name)];state=byid['NG'+str(code//10).zfill(2)]
 assert norm(name).startswith(norm(state['name'])),(name,state['name'])
 d={'id':'NBS-SD-'+str(code),'code':str(code),'code_system':'NBS MPI a1b (survey code; not INEC code)','name':name,'level':'senatorial district','state_id':state['id'],'metrics':poverty_metrics(n,'senatorial district'),'caveat':state['caveat']};districts.append(d)
 crosswalk.append({'from':d['id'],'to':state['id'],'relation':'state association only','validation':'validated against NBS code prefix and district/state names','source':'codes','year':2022,'can_allocate':False})
geo=json.loads((RAW/'lga.geojson').read_text());assert len(geo['features'])==774
lgas=[];health=json.loads((RAW/'health-counts.json').read_text());assert 'error' not in health and not health.get('exceededTransferLimit')
healthrows={ (norm(f['attributes']['state_standard']),norm(f['attributes']['lga_standard'])):f['attributes']['facilities'] for f in health['features']}
assert len(healthrows)==len(health['features'])
usedhealth=set()
for f in geo['features']:
 p=f['properties'];s=byname[norm(p['statename'])];code=str(p['lgacode']);id='GRID3-LGA-'+code
 a={'id':id,'name':p['lganame'],'level':'LGA','state_id':s['id'],'code':code,'code_system':'GRID3 lgacode','metrics':{}}
 key=(norm(p['statename']),norm(p['lganame']))
 if key in healthrows:a['metrics']['health']=measure(healthrows[key],'health','LGA',unit='listed facilities');usedhealth.add(key)
 f['properties']={'id':id,'name':a['name'],'state_id':s['id']};lgas.append(a)
 crosswalk.append({'from':id,'to':s['id'],'relation':'administrative membership','validation':'GRID3 state attribute and normalized exact state-name match','source':'lga','year':2021,'can_allocate':True})
assert len({a['id'] for a in lgas})==774
with rasterio.open(RAW/'population.tif') as raster:
 assert raster.crs.to_epsg()==4326
 grid=rasterize([(f['geometry'],i+1) for i,f in enumerate(geo['features'])],out_shape=raster.shape,transform=raster.transform,fill=0,dtype='uint16')
 values=raster.read(1);valid=(values!=raster.nodata)&np.isfinite(values)&(values>=0)
 sums=np.bincount(grid[valid].ravel(),weights=values[valid].ravel(),minlength=775)
 for i,a in enumerate(lgas):a['metrics']['population']=measure(round(float(sums[i+1])),'population','LGA',unit='people')
 population_coverage={'raster_total':round(float(sums.sum())),'assigned':round(float(sums[1:].sum())),'unassigned':round(float(sums[0])),'method':'Exclusive pixel-centre assignment; each pixel counted at most once. Do not treat unassigned raster population as zero.'}
for s in states:
 members=[a for a in lgas if a['state_id']==s['id']]
 s['metrics']['population']=measure(sum(a['metrics']['population']['value'] for a in members),'population','state',unit='people')
 s['metrics']['lgas']=measure(len(members),'lga','state',unit='LGAs')
 # State totals use all publisher state attributes, even where an LGA name is unmatched.
 s['metrics']['health']=measure(sum(n for (st,lga),n in healthrows.items() if st==norm(s['name'])),'health','state',unit='listed facilities')
projecttext=(RAW/'projects.txt').read_text();page=next(p for p in projecttext.split('\f') if 'ERGPs State' in p and 'ZIPs State' in p)
project_states=set()
for line in page.splitlines():
 matches=list(re.finditer(r'(\d+)\s+([A-Za-z][A-Za-z ]*?)\s+([\d.]+)(bn|tn)',line))
 if not matches or matches[-1].start()<130:continue
 count,name,amount,unit=matches[-1].groups();s=byname[norm(name)];project_states.add(s['id'])
 s['metrics']['project_budget']=measure(round(float(amount)*(1e12 if unit=='tn' else 1e9)),'projects','state',unit='NGN allocated')
 s['metrics']['projects']=measure(int(count),'projects','state',unit='budgeted ZIPs')
assert len(project_states)==37,len(project_states)
programmes=[]
db=Path('/opt/openg2p-lab/registration')
# Read only specific aggregate snapshots; do not open profiles, applications or sessions.
dbfiles=[db/'intake.sqlite']
for file in dbfiles:
 try:
  conn=sqlite3.connect('file:'+str(file)+'?mode=ro',uri=True)
  for source,metric in [('PBMS','programme_status'),('PBMS','beneficiary_list_workflow')]:
   row=conn.execute('SELECT payload,refreshed_at FROM analytics_source_cache WHERE source=?',(source,)).fetchone()
   if row:
    for item in json.loads(row[0]).get(metric,[]):
     assert isinstance(item['value'],(int,float))
     programmes.append({'name':metric.replace('_',' ').title()+': '+item['label'],'metric':measure(item['value'],'programme','installation-wide',unit='records',as_of=row[1])})
  row=conn.execute("SELECT payload,refreshed_at FROM analytics_source_cache WHERE source='Geographic record data'").fetchone()
  if row:
   for item in json.loads(row[0]).get('households_by_state',[]):
    s=byname.get(norm(item['label']))
    if s:s['metrics']['registry_households']=measure(item['value'],'programme','state',unit='sandbox households',as_of=row[1])
  conn.close();break
 except sqlite3.DatabaseError:continue
assert programmes,'Expected allowlisted programme aggregate snapshot'
projects=[{'id':'ERGP202302166','name':'Township road construction, Idanre LGA','state_id':byname['ondo']['id'],'district_id':next(d['id'] for d in districts if d['name']=='Ondo Central'),'allocation':measure(100000000,'projects','named project',unit='NGN allocated'),'year':2023,'status':'Budget allocation only; delivery and payment status not verified','mapping':'Named Ondo Central district in published project description; does not establish an LGA-wide electoral mapping.'}]
data={'version':1,'built_at':stamp,'sources':sources,'states':states,'lgas':lgas,'districts':districts,'crosswalk':crosswalk,'programmes':programmes,'projects':projects,'coverage':{'population':population_coverage,'health_unmatched_lgas':[{'state':a,'lga':b,'count':healthrows[(a,b)]} for a,b in sorted(set(healthrows)-usedhealth)],'district_boundary_mappings':0,'federal_constituencies_loaded':0,'state_constituencies_loaded':0,'project_register':'One source-verified example plus 37 state-level ZIP summaries; not a national project register.'},'gaps':['Federal and State Assembly constituency profiles and INEC identifiers await verified source acquisition.','No validated LGA/ward-to-constituency crosswalk or constituency polygons loaded. State association is not a spatial allocation rule.','No constituency GDP, GVA, income, employment, or live treasury feed is asserted.','Population, poverty, facilities and budgets refer to different years; they are not a synchronized current snapshot.']}
from territory_economy import add_economy
add_economy(data,RAW)
from territory_state_reports import add_state_reports
add_state_reports(data,RAW)
from territory_representatives import add_representatives
add_representatives(data,RAW)
(OUT/'data.json').write_text(json.dumps(data,separators=(',',':')))
(OUT/'lgas.geojson').write_text(json.dumps(geo,separators=(',',':')))
(OUT/'states.geojson').write_bytes((ROOT/'registration-ui/nigeria-states.geojson').read_bytes())
with (OUT/'measures.csv').open('w',newline='') as f:
 writer=csv.writer(f);writer.writerow(['area_id','area_name','measure','value','unit','source','source_url','reference_year','geographic_level','classification','confidence_lower','confidence_upper','qualification'])
 for area in states+lgas+districts:
  for key,m in area['metrics'].items():
   writer.writerow([area['id'],area['name'],key,m['value'],m['unit'],sources[m['source']]['name'],sources[m['source']]['url'],m['year'],m['level'],m['classification'],*m.get('ci',['','']),' '.join(filter(None,[area.get('caveat',''),m.get('qualification','')]))])
manifest={'built_at':stamp,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RAW.iterdir() if p.is_file() and p.suffix in ['.pdf','.json','.geojson','.tif','.html']},'records':{'states':len(states),'lgas':len(lgas),'districts':len(districts),'state_project_summaries':len(project_states)},'population':population_coverage,'health_unmatched':len(set(healthrows)-usedhealth)}
(ROOT/'territory-data/build-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
