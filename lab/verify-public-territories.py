"""External anonymous smoke test; no credentials or cookies supplied."""
import requests,json
base='https://nigeriag2p.com'
s=requests.Session();s.cookies.clear()
for path in ['/territories/','/territories/data.json','/territories/states.geojson','/territories/lgas.geojson','/territories/measures.csv']:
 r=s.get(base+path,timeout=30,allow_redirects=False)
 assert r.status_code==200,(path,r.status_code)
 assert 'Set-Cookie' not in r.headers
 if path.endswith('data.json'):
  data=r.json();assert (len(data['states']),len(data['lgas']),len(data['districts']))==(37,774,109)
 if path=='/territories/':assert 'site-shell.js' not in r.text and 'territory-root' in r.text
 print(path,200,'anonymous')
r=s.get(base+'/territories',timeout=30,allow_redirects=False)
assert r.status_code==308 and r.headers['Location']==base+'/territories/'
assert s.get(base+'/registration/api/analytics',timeout=30,allow_redirects=False).status_code==401
print('PASS: public access, canonical URL, reviewed data, and private API isolation.')
