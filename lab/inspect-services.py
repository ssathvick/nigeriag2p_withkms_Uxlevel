import requests,subprocess
for service in ['commons-services-awe']:
 p=subprocess.run(['kubectl','-n','nigeria','get','svc',service,'-o','jsonpath={.spec.clusterIP}'],text=True,capture_output=True)
 if p.returncode:continue
 r=requests.get('http://'+p.stdout+'/openapi.json');print(service,r.status_code)
 if r.status_code==200:
  d=r.json();print({k:v for k,v in d['paths'].items() if any(t in k for t in ['reassign','decide','tasks','policies'])});__import__('pathlib').Path('/opt/openg2p-lab/'+service+'-openapi.json').write_text(__import__('json').dumps(d))
