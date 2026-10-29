"""Persistent local branding at the TLS gateway, without rewriting application code or API data."""
import pathlib,subprocess,shutil,datetime,re,json
base=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
lab=pathlib.Path('/opt/openg2p-lab')
branding=lab/'branding'; branding.mkdir(exist_ok=True)
for file in (base/'branding').iterdir():
 if file.is_file(): shutil.copy2(file,branding/file.name)
config=pathlib.Path('/etc/nginx/sites-available/openg2p-lab')
backup=lab/'branding-backup'; backup.mkdir(exist_ok=True)
if not (backup/'nginx-before-iqs.conf').exists(): shutil.copy2(config,backup/'nginx-before-iqs.conf')
if not (backup/'launcher-before-iqs.html').exists(): shutil.copy2(lab/'home/index.html',backup/'launcher-before-iqs.html')
snippet='''# IQS presentation branding; same-origin static assets retain CSP protections.
location ^~ /iqs-brand/ {
    alias /opt/openg2p-lab/branding/;
    add_header Cache-Control "no-cache";
    add_header X-Content-Type-Options nosniff;
}
sub_filter_once on;
sub_filter '</head>' '<link rel="stylesheet" href="/iqs-brand/iqs-brand.css"><script defer src="/iqs-brand/iqs-brand.js"></script></head>';
'''
pathlib.Path('/etc/nginx/snippets/iqs-brand.conf').write_text(snippet)
text=config.read_text()
if 'include /etc/nginx/snippets/iqs-brand.conf;' not in text:
 text=text.replace('    client_max_body_size','    include /etc/nginx/snippets/iqs-brand.conf;\n    client_max_body_size',1)
 text=text.replace(' index index.html;',' index index.html;\n include /etc/nginx/snippets/iqs-brand.conf;')
 text=text.replace('        proxy_http_version 1.1;','        proxy_http_version 1.1;\n        proxy_set_header Accept-Encoding "";')
 config.write_text(text)
p=subprocess.run(['nginx','-t'],capture_output=True,text=True)
if p.returncode: raise RuntimeError(p.stderr)
subprocess.run(['systemctl','reload','nginx'],check=True)
home=(backup/'launcher-before-iqs.html').read_text()
home=home.replace('OpenG2P', 'IQS')
home=home.replace('<h1>Nigeria IQS Lab</h1>','<div class="iqs-logo-mark" role="img" aria-label="IQS"></div><h1>IQS Nigeria G2P</h1>')
home=home.replace('<html lang="en">','<html lang="en"><head>').replace('</style><main>','</style></head><body><main>').replace('</main></html>','</main></body></html>')
(lab/'home/index.html').write_text(home)
(base/'lab-home.html').write_text(home)
print('IQS gateway branding and login theme installed; nginx configuration valid.')
