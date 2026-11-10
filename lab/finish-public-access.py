import pathlib,json,subprocess,yaml
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/update-public-database-urls.py').read().split('targets=')[0])
sql('commons-postgresql','iam',"""
UPDATE staff_portal_applications SET active=false WHERE application_url IN ('https://g2p-keycloak.wverve.in','https://g2p-minio.wverve.in');
UPDATE staff_portal_applications SET application_url='https://g2p-master-data-ui.wverve.in' WHERE application_url='https://g2p-master-data.wverve.in';
UPDATE staff_portal_applications SET application_url='https://g2p-iam-staff-ui.wverve.in' WHERE application_url LIKE 'https://iam-staff-ui.%';
""")
origin=pathlib.Path('/etc/nginx/sites-available/iqs-public')
text=origin.read_text().replace('server_name g2p-pbms.wverve.in','server_name g2p-minio-api.wverve.in g2p-partner-register.wverve.in g2p-pbms.wverve.in')
origin.write_text(text)
p=pathlib.Path('/etc/cloudflared/config.yml');config=yaml.safe_load(p.read_text())
names=[r.get('hostname') for r in config['ingress']]
for h in ['g2p-minio-api.wverve.in','g2p-partner-register.wverve.in']:
 if h not in names:config['ingress'].insert(-1,{'hostname':h,'service':'http://127.0.0.1:18080'})
p.write_text(yaml.safe_dump(config,sort_keys=False));p.chmod(0o600)
subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
subprocess.run(['systemctl','restart','cloudflared'],check=True)
for h in ['g2p-minio-api.wverve.in','g2p-partner-register.wverve.in','*.nigeriag2p.com']:
 subprocess.run(['cloudflared','tunnel','route','dns','--overwrite-dns','iqs-nigeria-sandbox',h],check=True)
print('Supporting authenticated storage and partner APIs published; unmatched hosts return 404.')
