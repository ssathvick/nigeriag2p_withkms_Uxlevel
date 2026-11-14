import requests,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
s=requests.Session();s.verify='/opt/openg2p-lab/registration/ca-bundle.crt'
for name in ['awe','consent-manager']:
 base='https://g2p-'+name+'.wverve.in';r=s.get(base,timeout=25);soup=BeautifulSoup(r.text,'html.parser')
 for t in soup.select('script[src]'):
  code=s.get(urljoin(base,t['src']),timeout=25).text
  print(name,t['src'])
  for m in re.finditer(r'.{0,100}(?:/auth/|/api/auth|keycloak|/login|/me\b).{0,160}',code):print(m.group()[:260])
