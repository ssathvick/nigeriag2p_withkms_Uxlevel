import requests,json,datetime
for key in ['health','lga']:
 m=json.load(open('territory-data/raw/'+key+'-metadata.json'));print(key,'created',datetime.datetime.fromtimestamp(m['created']/1000),'modified',datetime.datetime.fromtimestamp(m['modified']/1000))
url='https://services3.arcgis.com/BU6Aadhn6tbBEdyk/arcgis/rest/services/Accessibility_Profile_by_State/FeatureServer/0'
m=requests.get(url,params={'f':'json'},timeout=30).json();print([(f['name'],f.get('alias')) for f in m.get('fields',[])]);print(m.get('description','')[:1500])
