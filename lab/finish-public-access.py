import pathlib,json,subprocess,yaml
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/update-public-database-urls.py').read().split('targets=')[0])
sql('commons-postgresql','iam',"""
UPDATE staff_portal_applications SET active=false WHERE application_url IN ('https://keycloak.nigeriag2p.com','https://minio.nigeriag2p.com');
UPDATE staff_portal_applications SET application_url='https://master-data-ui.nigeriag2p.com' WHERE application_url='https://master-data.nigeriag2p.com';
UPDATE staff_portal_applications SET application_url='https://iam-staff-ui.nigeriag2p.com' WHERE application_url LIKE 'https://iam-staff-ui.%';
""")
origin=pathlib.Path('/etc/nginx/sites-available/iqs-public')
text=origin.read_text().replace('server_name pbms.nigeriag2p.com','server_name minio-api.nigeriag2p.com partner-register.nigeriag2p.com pbms.nigeriag2p.com')
origin.write_text(text)
p=pathlib.Path('/etc/cloudflared/config.yml');config=yaml.safe_load(p.read_text())
names=[r.get('hostname') for r in config['ingress']]
for h in ['minio-api.nigeriag2p.com','partner-register.nigeriag2p.com']:
 if h not in names:config['ingress'].insert(-1,{'hostname':h,'service':'http://127.0.0.1:18080'})
p.write_text(yaml.safe_dump(config,sort_keys=False));p.chmod(0o600)
subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
subprocess.run(['systemctl','restart','cloudflared'],check=True)
for h in ['minio-api.nigeriag2p.com','partner-register.nigeriag2p.com','*.nigeriag2p.com']:
 subprocess.run(['cloudflared','tunnel','route','dns','--overwrite-dns','iqs-nigeria-sandbox',h],check=True)
print('Supporting authenticated storage and partner APIs published; unmatched hosts return 404.')
