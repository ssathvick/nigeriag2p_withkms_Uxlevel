"""Back up touched files, deploy simulator, enable callback worker, verify health."""
import datetime
import json
import shutil
import subprocess
import time
from pathlib import Path
import requests

src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
root=Path('/opt/openg2p-lab/registration')
backup=root/'simulation-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,mode=0o700)
targets=[(src/n,root/n) for n in ['registration_app.py','partner_simulation.py','simulation-worker.py','simulation-openapi.json']]
targets += [(src/'registration-ui'/n,root/'templates'/n) for n in ['base.html','analytics.html','simulation.html','simulation-run.html']]
manifest=[]
for i,(source,target) in enumerate(targets):
    saved=backup/str(i)
    if target.exists():shutil.copy2(target,saved)
    manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
(backup/'manifest.json').write_text(json.dumps(manifest))
subprocess.run(['systemctl','stop','iqs-registration.service'],check=True)
try:
    for source,target in targets:shutil.copy2(source,target)
    subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',str(root/'registration_app.py'),str(root/'partner_simulation.py')],check=True)
    subprocess.run(['systemctl','start','iqs-registration.service'],check=True)
    for _ in range(30):
        try:
            if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
        except requests.RequestException:pass
        time.sleep(.3)
    assert requests.get('http://127.0.0.1:18081/registration/health',timeout=3).status_code==200
    Path('/etc/systemd/system/iqs-simulation.service').write_text('''[Unit]
Description=Process synthetic G2P partner callbacks
After=iqs-registration.service
[Service]
Type=oneshot
WorkingDirectory=/opt/openg2p-lab/registration
ExecStart=/opt/openg2p-lab/registration-venv/bin/python /opt/openg2p-lab/registration/simulation-worker.py
UMask=0077
''')
    Path('/etc/systemd/system/iqs-simulation.timer').write_text('''[Unit]
Description=Poll synthetic G2P callbacks every ten seconds
[Timer]
OnBootSec=15s
OnUnitActiveSec=10s
AccuracySec=1s
[Install]
WantedBy=timers.target
''')
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','enable','--now','iqs-simulation.timer'],check=True)
    subprocess.run(['systemctl','start','iqs-simulation.service'],check=True)
    print('Simulation installed. Private file backup:',backup)
except Exception:
    subprocess.run(['systemctl','stop','iqs-simulation.timer'])
    for entry in manifest:
        target=Path(entry['target'])
        if entry['saved']:shutil.copy2(entry['saved'],target)
        elif target.exists():target.unlink()
    subprocess.run(['systemctl','start','iqs-registration.service'])
    raise
