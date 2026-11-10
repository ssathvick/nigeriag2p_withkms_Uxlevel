from pathlib import Path
import requests,json,concurrent.futures,subprocess
root=Path('territory-data/raw')
def fetch(name,url,params=None):
 p=root/name
 if not p.exists():
  r=requests.get(url,params=params,timeout=90);r.raise_for_status();p.write_bytes(r.content)
 print(name,p.stat().st_size)
 return p
jobs=[('population.tif','https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/NGA/nga_ppp_2020_1km_Aggregated_UNadj.tif',None),('lga.geojson',json.load(open(root/'lga-metadata.json'))['url']+'/0/query',{'f':'geojson','where':'1=1','outFields':'lganame,lgacode,statename,statecode,uniq_id','outSR':4326,'maxAllowableOffset':0.002,'geometryPrecision':5,'resultRecordCount':2000})]
for name in ['health']:
 url=json.load(open(root/(name+'-metadata.json')))['url']+'/0/query'
 jobs.append(('health-counts.json',url,{'f':'json','where':'1=1','groupByFieldsForStatistics':'state_standard,lga_standard','outStatistics':json.dumps([{'statisticType':'count','onStatisticField':'OBJECTID','outStatisticFieldName':'facilities'}]),'returnGeometry':'false','resultRecordCount':2000}))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures=[pool.submit(fetch,*j) for j in jobs]
 for f in futures:f.result()
