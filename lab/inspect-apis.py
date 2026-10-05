import subprocess,json,pathlib,requests
services=['commons-services-master-data-api','commons-services-iam-staff-portal-api','commons-services-awe','register-staff-portal-api','spar-openg2p-spar-mapper-api','bridge-api','pbms-api']
for name in services:
    ip=subprocess.check_output(['kubectl','get','svc',name,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    for path in ['/openapi.json','/v1/openapi.json','/v1/selfservice/openapi.json']:
        try:r=requests.get('http://'+ip+path,timeout=10)
        except requests.RequestException:continue
        if r.status_code==200 and 'paths' in r.json():
            pathlib.Path('/opt/openg2p-lab/'+name+'-openapi.json').write_text(r.text)
            print(name,list(r.json()['paths'])[:35],flush=True)
            break
