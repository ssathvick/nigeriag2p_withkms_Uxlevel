import datetime,json,pathlib,shutil,subprocess
root=pathlib.Path('/opt/openg2p-lab/pbms-react')
src=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/workflow_api.py')
target=root/'adapter/workflow_api.py';target.parent.mkdir(exist_ok=True)
backup=root/'backups'/('adapter-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
unit=pathlib.Path('/etc/systemd/system/pbms-react-api.service')
env=root/'adapter/service.env'
for p in [target,unit,env]:
    if p.exists():shutil.copy2(p,backup/p.name)
def ip(name):return subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
shutil.copy2(src,target);target.chmod(0o644)
env.write_text('PBMS_ODOO_URL=http://'+ip('pbms-odoo')+'\nPBMS_BRIDGE_URL=http://'+ip('bridge-api')+'\n')
env.chmod(0o644)
unit.write_text('''[Unit]
Description=PBMS React authenticated workflow adapter
After=k3s.service network.target
Wants=k3s.service
[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/openg2p-lab/pbms-react/adapter
EnvironmentFile=/opt/openg2p-lab/pbms-react/adapter/service.env
RuntimeDirectory=pbms-react
RuntimeDirectoryMode=0700
ExecStart=/opt/openg2p-lab/registration-venv/bin/gunicorn --workers 2 --threads 4 --timeout 120 --bind 127.0.0.1:18112 workflow_api:app
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
[Install]
WantedBy=multi-user.target
''')
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','pbms-react-api'],check=True,capture_output=True)
subprocess.run(['systemctl','restart','pbms-react-api'],check=True)
subprocess.run(['systemctl','is-active','pbms-react-api'],check=True)
print('Adapter installed; existing backend services unchanged. Backup:',backup)
