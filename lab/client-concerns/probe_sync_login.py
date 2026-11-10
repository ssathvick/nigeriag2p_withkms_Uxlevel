import sys,requests,json
from pathlib import Path
from html.parser import HTMLParser
class Form(HTMLParser):
 def handle_starttag(self,tag,a):
  d=dict(a)
  if tag=='form' and 'action' in d:self.action=d['action']
s=requests.Session();s.verify='/opt/openg2p-lab/registration/ca-bundle.crt'
r=s.get('https://odk.nigeriag2p.com/v1/oidc/login',timeout=30)
p=Form();p.feed(r.text);print('ODK login',r.status_code,'action',hasattr(p,'action'))
# Only inspect public response keys, never credential values.
r=s.get('https://register.nigeriag2p.com/api/auth/providers',timeout=30);print('Registry providers',r.status_code,r.text[:300])
