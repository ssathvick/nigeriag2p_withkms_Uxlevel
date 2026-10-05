"""Install the persistent WSL intake integration and its OIDC clients."""
import json,subprocess,pathlib,shutil,os,yaml,requests
SRC=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');ROOT=pathlib.Path('/opt/openg2p-lab/registration');ROOT.mkdir(exist_ok=True)
def run(*args):return subprocess.check_output(args,text=True).strip()
pwd=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
kc='http://'+run('kubectl','-n','nigeria','get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}')
r=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':pwd},timeout=20);r.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+r.json()['access_token']
config={'base_url':'https://nigeriag2p.com','keycloak':'https://keycloak.nigeriag2p.com','clients':{}}
for mode,realm in [('beneficiary','beneficiary'),('staff','staff')]:
 url=kc+'/admin/realms/'+realm;client='iqs-registration-'+mode
 ids=s.get(url+'/clients',params={'clientId':client}).json()
 values={'clientId':client,'name':'IQS Registration '+mode.title(),'enabled':True,'publicClient':False,'standardFlowEnabled':True,'directAccessGrantsEnabled':False,'serviceAccountsEnabled':False,'redirectUris':['https://nigeriag2p.com/registration/callback'],'webOrigins':['https://nigeriag2p.com'],'attributes':{'pkce.code.challenge.method':'S256'}}
 if not ids:s.post(url+'/clients',json=values).raise_for_status();ids=s.get(url+'/clients',params={'clientId':client}).json()
 else:s.put(url+'/clients/'+ids[0]['id'],json=values).raise_for_status()
 secret=s.get(url+'/clients/'+ids[0]['id']+'/client-secret').json()['value'];config['clients'][mode]={'id':client,'secret':secret}
 if mode=='beneficiary':
  s.put(url,json={'registrationAllowed':True,'registrationEmailAsUsername':False,'duplicateEmailsAllowed':False,'bruteForceProtected':True,'passwordPolicy':'length(10)','displayName':'IQS Nigeria Beneficiary Sandbox'}).raise_for_status()
 else:
  role='iqs-intake-reviewer';rr=s.get(url+'/roles/'+role)
  if rr.status_code==404:s.post(url+'/roles',json={'name':role,'description':'Review IQS synthetic household registrations and programme enrollment'}).raise_for_status();rr=s.get(url+'/roles/'+role)
  rr.raise_for_status();user=s.get(url+'/users',params={'username':'admin','exact':'true'}).json()[0]
  s.post(url+'/users/'+user['id']+'/role-mappings/realm',json=[rr.json()]).raise_for_status()
(ROOT/'config.json').write_text(json.dumps(config));os.chmod(ROOT/'config.json',0o600)
shutil.copy2(SRC/'registration_app.py',ROOT/'registration_app.py')
(ROOT/'templates').mkdir(exist_ok=True);(ROOT/'static').mkdir(exist_ok=True)
for f in (SRC/'registration-ui').glob('*.html'):shutil.copy2(f,ROOT/'templates'/f.name)
shutil.copy2(SRC/'registration-ui/style.css',ROOT/'static/style.css')
(ROOT/'ca-bundle.crt').write_bytes(pathlib.Path('/etc/ssl/certs/ca-certificates.crt').read_bytes()+b'\n'+pathlib.Path('/opt/openg2p-lab/tls/ca.crt').read_bytes())
unit='''[Unit]
Description=IQS Nigeria beneficiary registration and integration
After=k3s.service nginx.service
Wants=k3s.service
[Service]
WorkingDirectory=/opt/openg2p-lab/registration
Environment=REQUESTS_CA_BUNDLE=/opt/openg2p-lab/registration/ca-bundle.crt
Environment=SSL_CERT_FILE=/opt/openg2p-lab/registration/ca-bundle.crt
UMask=0077
ExecStart=/opt/openg2p-lab/registration-venv/bin/gunicorn --workers 1 --threads 4 --timeout 120 --bind 127.0.0.1:18081 registration_app:app
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
'''
pathlib.Path('/etc/systemd/system/iqs-registration.service').write_text(unit)
pathlib.Path('/etc/systemd/system/iqs-registration-sync.service').write_text('''[Unit]
Description=Reconcile IQS registry and programme applications
After=k3s.service iqs-registration.service
[Service]
Type=oneshot
WorkingDirectory=/opt/openg2p-lab/registration
Environment=REQUESTS_CA_BUNDLE=/opt/openg2p-lab/registration/ca-bundle.crt
Environment=SSL_CERT_FILE=/opt/openg2p-lab/registration/ca-bundle.crt
UMask=0077
ExecStart=/opt/openg2p-lab/registration-venv/bin/python registration_app.py --reconcile
TimeoutStartSec=120
''')
pathlib.Path('/etc/systemd/system/iqs-registration-sync.timer').write_text('''[Unit]
Description=IQS integration reconciliation every minute
[Timer]
OnBootSec=90s
OnUnitActiveSec=60s
Unit=iqs-registration-sync.service
[Install]
WantedBy=timers.target
''')
ng=pathlib.Path('/etc/nginx/sites-available/iqs-public');t=ng.read_text()
location=''' location ^~ /registration/ {
  if ($host = www.nigeriag2p.com) { return 308 https://nigeriag2p.com$request_uri; }
  client_max_body_size 64k;
  proxy_pass http://127.0.0.1:18081;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-Proto https;
  proxy_read_timeout 120s;
 }
 location = /registration { return 302 /registration/; }
'''
if 'location ^~ /registration/' not in t:t=t.replace(' location / { try_files $uri $uri/ =404; }',location+' location / { try_files $uri $uri/ =404; }')
if 'if ($host = www.nigeriag2p.com)' not in t:t=t.replace(' location ^~ /registration/ {',' location ^~ /registration/ {\n  if ($host = www.nigeriag2p.com) { return 308 https://nigeriag2p.com$request_uri; }')
ng.write_text(t);subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
for home in ['/opt/openg2p-lab/public-home/index.html','/opt/openg2p-lab/home/index.html']:
 p=pathlib.Path(home);html=p.read_text()
 if 'Beneficiary &amp; household registration' not in html:
  cards='<a class="card" href="https://nigeriag2p.com/registration/"><h2>Beneficiary &amp; household registration</h2><p>Create an account, register a household, apply for integrated programmes and track enrollment.</p></a>\n<a class="card" href="https://nigeriag2p.com/registration/login?mode=staff"><h2>Registration &amp; enrollment review</h2><p>Staff: approve registrations, create connected programmes, check eligibility and confirm enrollment.</p></a>\n'
  html=html.replace('<div class="grid">','<div class="grid">\n'+cards);p.write_text(html)
subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','enable','--now','iqs-registration.service','iqs-registration-sync.timer'],check=True)
print('Registration integration installed. OIDC signup enabled for beneficiary realm only. Reviewer assigned to existing staff administrator.')
