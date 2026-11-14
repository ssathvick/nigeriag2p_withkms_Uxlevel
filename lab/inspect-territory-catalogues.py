import requests,json
for term in ['GRID3 NGA Operational LGA Boundaries','GRID3 NGA Health Facilities v2.0','GRID3 Nigeria Ward Boundaries']:
 r=requests.get('https://www.arcgis.com/sharing/rest/search',params={'q':term,'f':'json','num':8},timeout=30).json()
 print(json.dumps([{'id':x['id'],'title':x['title'],'url':x.get('url'),'owner':x['owner']} for x in r.get('results',[])],indent=2))
