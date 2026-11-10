"""Install the React PBMS entry point with a transactional Nginx rollback."""
from pathlib import Path
import datetime, shutil, subprocess, json

source = Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/dist')
root = Path('/opt/openg2p-lab/pbms-react')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
release = root / 'releases' / stamp
backup = root / 'backups' / stamp
backup.mkdir(parents=True, mode=0o700)
config = Path('/etc/nginx/sites-available/iqs-wverve')
tls_config = Path('/etc/nginx/sites-available/openg2p-lab')
dedicated = Path('/etc/nginx/conf.d/pbms-react.conf')
for name in ['index.html','app.js','app.css']:
    assert (source/name).is_file(), name
old_config = config.read_text()
old_tls_config = tls_config.read_text()
old_dedicated = dedicated.read_text() if dedicated.exists() else None
current = root/'current'
old_release = str(current.resolve()) if current.exists() else None
(backup/'iqs-wverve').write_text(old_config)
(backup/'openg2p-lab').write_text(old_tls_config)
if old_dedicated is not None:
    (backup/'pbms-react.conf').write_text(old_dedicated)
(backup/'manifest.json').write_text(json.dumps({'previous_release':old_release,'dedicated_existed':old_dedicated is not None},indent=2))
shutil.copytree(source,release)
new_config = old_config.replace(' g2p-pbms.wverve.in ', ' ')
assert 'server_name g2p-minio-api.wverve.in' in new_config
new_dedicated = '''# PBMS React frontend. Native routes continue to the existing backend.
server {
 listen 443 ssl;
 server_name g2p-pbms.wverve.in pbms.openg2p.localhost;
 ssl_certificate /opt/openg2p-lab/tls/server.crt;
 ssl_certificate_key /opt/openg2p-lab/tls/server.key;
 client_max_body_size 100m;
 large_client_header_buffers 4 32k;
 location / {
  proxy_pass http://127.0.0.1:18080;
  proxy_set_header Host g2p-pbms.wverve.in;
  proxy_set_header X-Forwarded-Proto https;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_buffer_size 32k;
  proxy_buffers 8 32k;
  proxy_redirect https://g2p-pbms.wverve.in/ https://$host/;
  proxy_read_timeout 300s;
 }
}
server {
 listen 127.0.0.1:18080;
 server_name g2p-pbms.wverve.in;
 absolute_redirect off;
 client_max_body_size 100m;
 large_client_header_buffers 4 32k;
 location = / { return 302 /pbms-ui/; }
 location = /web {
  if ($arg_native != 1) { return 302 /pbms-ui/; }
  proxy_pass http://127.0.0.1:30080;
  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-Proto https;
  proxy_set_header X-Forwarded-Host $host;
  proxy_buffer_size 32k;
  proxy_buffers 8 32k;
 }
 location = /iqs-brand/knowledge {
  proxy_pass http://127.0.0.1:18081/registration/api/knowledge;
  proxy_set_header Host g2p.wverve.in;
  proxy_set_header Cookie "";
  proxy_hide_header Set-Cookie;
 }
 location ^~ /iqs-brand/ {
  alias /opt/openg2p-lab/branding/;
  add_header Cache-Control "no-cache";
  add_header X-Content-Type-Options nosniff;
 }
 location = /pbms-ui { return 302 /pbms-ui/; }
 location ^~ /pbms-ui-api/ {
  proxy_pass http://127.0.0.1:18112;
  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-Proto https;
  proxy_read_timeout 120s;
  client_max_body_size 16m;
 }
 location ^~ /pbms-ui/ {
  alias /opt/openg2p-lab/pbms-react/current/;
  index index.html;
  add_header Cache-Control "no-store" always;
  add_header X-Content-Type-Options nosniff always;
  add_header Referrer-Policy same-origin always;
  add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'" always;
 }
 location ^~ /web/database/ { return 404; }
 location / {
  proxy_pass http://127.0.0.1:30080;
  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_set_header X-Forwarded-Proto https;
  proxy_set_header X-Forwarded-Host $host;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_buffer_size 32k;
  proxy_buffers 8 32k;
  proxy_redirect http:// https://;
  proxy_read_timeout 300s;
 }
}
'''
try:
    config.write_text(new_config)
    tls_config.write_text(old_tls_config.replace(' g2p-pbms.wverve.in ', ' '))
    dedicated.write_text(new_dedicated)
    temporary = root/'next'
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(release, target_is_directory=True)
    temporary.replace(current)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
except Exception:
    config.write_text(old_config)
    tls_config.write_text(old_tls_config)
    if old_dedicated is None:
        dedicated.unlink(missing_ok=True)
    else:
        dedicated.write_text(old_dedicated)
    current.unlink(missing_ok=True)
    if old_release:
        current.symlink_to(old_release, target_is_directory=True)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
    raise
print(json.dumps({'release':str(release),'rollback':str(backup),'entry':'https://pbms.nigeriag2p.com/pbms-ui/'}))
