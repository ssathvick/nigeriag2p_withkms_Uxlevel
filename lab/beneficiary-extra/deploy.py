from pathlib import Path
import datetime,json,secrets,shutil,sqlite3,subprocess
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/beneficiary-extra');root=Path('/opt/openg2p-lab/beneficiary-extra');root.mkdir(exist_ok=True)
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=root/'backups'/stamp;backup.mkdir(parents=True)
nginx=Path('/etc/nginx/sites-available/iqs-wverve');snippet=Path('/etc/nginx/snippets/iqs-brand.conf');dedicated=Path('/etc/nginx/conf.d/beneficiary-extra.conf')
paths=[nginx,snippet,dedicated,root/'server.py',root/'config.json',Path('/etc/systemd/system/iqs-beneficiary-extra.service')]
for p in paths:
 if p.exists():shutil.copy2(p,backup/p.name)
for name in ['intake.sqlite','phase1-sandbox.sqlite']:
 with sqlite3.connect('/opt/openg2p-lab/registration/'+name) as c,sqlite3.connect(backup/name) as b:c.backup(b)
def svc(name):return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
config={'jwks':svc('commons-keycloak')+'/realms/beneficiary/protocol/openid-connect/certs','keymanager':svc('commons-services-keymanager'),'mapper':svc('spar-openg2p-spar-mapper-api'),'secret':json.loads((root/'config.json').read_text())['secret'] if (root/'config.json').exists() else secrets.token_urlsafe(48)}
(root/'config.json').write_text(json.dumps(config));(root/'config.json').chmod(0o600)
shutil.copy2(src/'server.py',root/'server.py');shutil.copytree(src/'dist',root/'dist',dirs_exist_ok=True)
shutil.copy2(src/'navigation.js','/opt/openg2p-lab/branding/beneficiary-navigation.js')
service=Path('/etc/systemd/system/iqs-beneficiary-extra.service')
service.write_text('''[Unit]
Description=NSIPA beneficiary frontend adapter
After=network.target iqs-registration.service
[Service]
WorkingDirectory=/opt/openg2p-lab/beneficiary-extra
ExecStart=/opt/openg2p-lab/registration-venv/bin/gunicorn --workers 2 --threads 4 --timeout 120 --bind 127.0.0.1:18115 server:app
Restart=on-failure
UMask=0077
NoNewPrivileges=true
[Install]
WantedBy=multi-user.target
''')
subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','enable','--now','iqs-beneficiary-extra'],check=True);subprocess.run(['systemctl','restart','iqs-beneficiary-extra'],check=True)
new='''server {
 listen 127.0.0.1:18080;
 server_name g2p-beneficiary.wverve.in;
 absolute_redirect off;
 large_client_header_buffers 4 32k;
 proxy_cookie_domain nigeriag2p.com wverve.in;
 include /etc/nginx/snippets/iqs-brand.conf;
 location ^~ /beneficiary-api/ {
  proxy_pass http://127.0.0.1:18115;
  proxy_set_header Host $host;
  proxy_read_timeout 120s;
  client_max_body_size 16k;
 }
 location ^~ /beneficiary-extra/ {
  alias /opt/openg2p-lab/beneficiary-extra/dist/;
  add_header Cache-Control "no-cache";
 }
 location ~ ^/selfservice/en/(accounts|complaints|notifications|news|registries)/?$ {
  root /opt/openg2p-lab/beneficiary-extra/dist;
  try_files /index.html =404;
  sub_filter '</head>' '</head>';
  add_header Cache-Control "no-store" always;
  add_header X-Content-Type-Options nosniff always;
  add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'" always;
 }
 location / {
  proxy_pass http://127.0.0.1:30080;
  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_set_header Accept-Encoding "identity";
  proxy_set_header X-Forwarded-Proto https;
  proxy_set_header X-Forwarded-Host $host;
  proxy_buffer_size 32k;
  proxy_buffers 8 32k;
  proxy_redirect http:// https://;
  proxy_read_timeout 300s;
 }
}
'''
try:
 nginx.write_text(nginx.read_text().replace(' g2p-beneficiary.wverve.in ', ' '));dedicated.write_text(new)
 text=snippet.read_text()
 if 'beneficiary-navigation.js' not in text:text=text.replace('</head>\';','<script defer src="/iqs-brand/beneficiary-navigation.js"></script></head>\';')
 snippet.write_text(text)
 subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
except Exception:
 for p in [nginx,snippet,dedicated]:
  if (backup/p.name).exists():shutil.copy2(backup/p.name,p)
  elif p==dedicated:p.unlink(missing_ok=True)
 subprocess.run(['systemctl','reload','nginx']);raise
print('Deployed. Backup:',backup)
