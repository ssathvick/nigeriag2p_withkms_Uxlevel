"""Install NSIPA presentation assets with a private rollback snapshot."""
from pathlib import Path
import shutil, subprocess, datetime, re, json
source=Path(__file__).resolve().parent
root=Path('/opt/openg2p-lab')
backup=root/'nsipa-branding-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,mode=0o700)
snippet=Path('/etc/nginx/snippets/iqs-brand.conf')
for name in ['branding','home','public-home','registration/templates','registration/static']:
    shutil.copytree(root/name,backup/name)
shutil.copy2(snippet,backup/'iqs-brand.conf')

try:
    for name in ['iqs-brand.js','iqs-brand.css','iqs-logo.png','nsipa-logo.png','nsipa-logo.svg','nsipa-symbol.svg','nsipa-wordmark.svg']:
        shutil.copy2(source/'branding'/name,root/'branding'/name)
    for name in ['site.js','site-shell.js']:
        shutil.copy2(source/'persona-ui/dist'/name,root/'branding'/name)
    shutil.copy2(source/'persona-ui/dist/workspace.js',root/'registration/static/workspace.js')
    for name in ['home','public-home']:
        shutil.copy2(source/'sitewide-ui/index.html',root/name/'index.html')
    for path in (root/'registration/templates').glob('*.html'):
        text=path.read_text()
        text=text.replace('/iqs-brand/iqs-logo.png','/iqs-brand/nsipa-wordmark.svg').replace('IQS — IQ Systems Solutions','NSIPA — National Social Investment Programmes Agency').replace('IQS Nigeria','NSIPA Nigeria').replace('NigeriaG2P','NSIPA')
        text=re.sub(r'workspace\.js(?:\?[^"\s]*)?', 'workspace.js?v=nsipa-20261103-r3',text)
        path.write_text(text)
    text=snippet.read_text()
    for asset in ['iqs-brand.js','iqs-brand.css','site-shell.js','site-shell.css']:
        text=re.sub(re.escape('/iqs-brand/'+asset)+r'(?:\?[^"\s]*)?', '/iqs-brand/'+asset+'?v=nsipa-20261103-r3',text)
    # Serve the approved vector mark at vendor logo URLs as well, covering
    # CSS backgrounds and pre-JavaScript image requests. No API paths change.
    if '# NSIPA vendor logo aliases' not in text:
        text += '''
# NSIPA vendor logo aliases (presentation assets only).
location ~* /(?:[^/]*(?:openg2p|keycloak|odk|superset|minio|redpanda|odoo)[^/]*(?:logo|favicon)[^/]*|[^/]*(?:logo|favicon)[^/]*(?:openg2p|keycloak|odk|superset|minio|redpanda|odoo)[^/]*|keycloak|logo(?:[_-](?:bw|horizontal|vertical|1))?)\\.(?:svg|png|webp)$ {
    alias /opt/openg2p-lab/branding/nsipa-wordmark.svg;
    types { } default_type image/svg+xml;
    add_header Cache-Control "no-cache";
}
location = /favicon.ico {
    alias /opt/openg2p-lab/branding/nsipa-symbol.svg;
    types { } default_type image/svg+xml;
    add_header Cache-Control "no-cache";
}
'''
    snippet.write_text(text)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
    # Jinja templates are cached by the existing application workers.
    subprocess.run(['systemctl','restart','iqs-registration'],check=True)
except Exception:
    for name in ['branding','home','public-home','registration/templates','registration/static']:
        shutil.copytree(backup/name,root/name,dirs_exist_ok=True)
    shutil.copy2(backup/'iqs-brand.conf',snippet)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
    subprocess.run(['systemctl','restart','iqs-registration'],check=True)
    raise
print('NSIPA shared theme installed. Rollback snapshot:',backup)
