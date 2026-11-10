import json,subprocess,requests
from pathlib import Path
out=Path(__file__).parent/'beneficiary-capabilities.json';results={}
for name in ['pbms-beneficiary-portal','spar-openg2p-spar-mapper-api','commons-services-cm-api']:
 ip=subprocess.check_output(['kubectl','get','svc','-n','nigeria',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
 try:
  r=requests.get('http://'+ip+'/openapi.json',timeout=20);r.raise_for_status();d=r.json();results[name]=d
  print(name,json.dumps({p:list(v) for p,v in d.get('paths',{}).items()},indent=1))
 except Exception as e:print(name,type(e).__name__)
out.write_text(json.dumps(results,indent=2))
