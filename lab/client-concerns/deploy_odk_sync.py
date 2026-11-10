from pathlib import Path
import shutil,subprocess,json,hashlib,sys
src=Path(__file__).parent;dest=Path('/opt/openg2p-lab/odk-sync')
for name in ['odk_sync_worker.py','odk_household_mapping.py','odk_legacy_mapping.py']:shutil.copy2(src/name,dest/name)
cfg=json.loads((dest/'config.json').read_text())
cfg['definition_sha256']={form:hashlib.sha256((src/'odk-verification'/file).read_bytes()).hexdigest() for form,file in [('nsipa_field_household_demo','0-current-definition.xml'),('nsipa_household_mapping_check','0-numeric-definition.xml')]}
(dest/'config.json').write_text(json.dumps(cfg));(dest/'config.json').chmod(0o600)
unit='''[Unit]
Description=NSIPA ODK to registry intake synchronization (no approval permission)
After=network-online.target k3s.service
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/openg2p-lab/odk-sync
ExecStart=/opt/openg2p-lab/registration-venv/bin/python /opt/openg2p-lab/odk-sync/odk_sync_worker.py
UMask=0077
TimeoutStartSec=240
NoNewPrivileges=true
PrivateTmp=true
'''
timer='''[Unit]
Description=Poll ODK for NSIPA intake submissions every minute

[Timer]
OnBootSec=90
OnUnitInactiveSec=60
AccuracySec=1
Unit=nsipa-odk-sync.service

[Install]
WantedBy=timers.target
'''
for name,text in [('nsipa-odk-sync.service',unit),('nsipa-odk-sync.timer',timer)]:
 (Path('/etc/systemd/system')/name).write_text(text);(src/name).write_text(text)
subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','enable','--now','nsipa-odk-sync.timer'],check=True)
print('Enabled persistent systemd timer; shared ledger and private credentials retained.')
