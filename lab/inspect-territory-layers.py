import requests,json
from pathlib import Path
root=Path('territory-data/raw')
items={'lga':'2bb616a49ee84f409427cc2143787113','health':'9df52e12d0b5422f8f73c44d0dc91f8b','ward':'74cf76766bec4481aa03523e0e1fdddc'}
for key,id in items.items():
 meta=requests.get(f'https://www.arcgis.com/sharing/rest/content/items/{id}',params={'f':'json'},timeout=30).json();(root/(key+'-metadata.json')).write_text(json.dumps(meta))
 service=requests.get(meta['url'],params={'f':'json'},timeout=30).json();print(key,'description',meta.get('description','')[:3500],'license',meta.get('licenseInfo'), 'layers',service.get('layers'))
 for layer in service.get('layers',[])[:1]:
  url=meta['url']+'/'+str(layer['id']); detail=requests.get(url,params={'f':'json'},timeout=30).json();(root/(key+'-layer.json')).write_text(json.dumps(detail));print('FIELDS',[(f['name'],f.get('alias')) for f in detail.get('fields',[])])
