import requests
s=requests.Session();s.verify='/opt/openg2p-lab/registration/ca-bundle.crt'
for n in ['awe','consent-manager']:
 r=s.get('https://g2p-'+n+'.wverve.in/config.json');print(n,r.status_code,r.text[:2500])
