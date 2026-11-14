import subprocess,json,urllib.request
ip=subprocess.check_output(['kubectl','-n','nigeria','get','svc','commons-services-master-data-api','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
try:
 doc=json.load(urllib.request.urlopen('http://'+ip+'/openapi.json'));print([p for p in doc.get('paths',{}) if 'attribute' in p])
except Exception as e:print(type(e).__name__,str(e)[:100])
