import sys,subprocess,json,requests
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
print(query('mosip_keymgr',"SELECT table_schema,table_name FROM information_schema.tables WHERE table_name LIKE '%key%';"))
for service in ['commons-services-keymanager','spar-openg2p-spar-mapper-api','bridge-api','openg2p-g2p-bridge-example-bank-api']:
 ip=subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
 for path in ['/openapi.json','/v1/keymanager/swagger.json']:
  r=requests.get('http://'+ip+path,timeout=15)
  if r.status_code==200 and 'paths' in r.json():
   open('/opt/openg2p-lab/'+service+'-openapi.json','w').write(r.text)
   print(service,'routes',list(r.json()['paths'])[:25]);break
