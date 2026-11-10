"""Deploy only tested sandbox files, retain private backup and rollback on failure."""
import datetime as dt
import hashlib
import json
import shutil
import sqlite3
import subprocess
import time
from pathlib import Path
import requests
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration')
baseline='47cc902b559d680e1f31e04d2e40458cacd72faba83f7f16bd9eb0b96842fc91'
runtime_hash=hashlib.sha256((root/'registration_app.py').read_bytes()).hexdigest()
source_hash=hashlib.sha256((src/'registration_app.py').read_bytes()).hexdigest()
if runtime_hash not in (baseline,source_hash):raise RuntimeError('Runtime changed since inspection; reconcile before deployment.')
targets=[(src/name,root/name) for name in ['registration_app.py','phase1_sandbox.py','phase1_cms.py','phase1_observability.py','phase1_conditionality.py','phase1-worker.py']]
targets += [(src/'registration-ui'/name,root/'templates'/name) for name in ['base.html','phase1.html','phase1-field.html','phase1-public.html','phase1-cms.html','phase1-grievances.html','phase1-readiness.html','phase1-conditionality.html']]
targets += [(src/'knowledge'/name,root/'static'/name) for name in ['phase1-field.js','phase1-sw.js','phase1-portal.css']]
targets += [(src/'persona-ui/dist/site.js',Path('/opt/openg2p-lab/branding/site.js'))]
targets += [(src/'persona-ui/dist/site-shell.js',Path('/opt/openg2p-lab/branding/site-shell.js'))]
targets += [(src/'knowledge/help.js',Path('/opt/openg2p-lab/branding/knowledge-help.js'))]
targets += [(src/'sitewide-ui/index.html',Path('/opt/openg2p-lab')/folder/'index.html') for folder in ['public-home','home']]
backup=root/'phase1-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
manifest=[]
for i,(source,target) in enumerate(targets):
    if not source.is_file():raise RuntimeError('Missing source: '+str(source))
    saved=backup/str(i)
    if target.exists():shutil.copy2(target,saved)
    manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
units=[Path('/etc/systemd/system/iqs-phase1.service'),Path('/etc/systemd/system/iqs-phase1.timer')]
for i,target in enumerate(units):
    saved=backup/('unit-'+str(i))
    if target.exists():shutil.copy2(target,saved)
    manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
subprocess.run(['systemctl','stop','iqs-registration.service'],check=True)
try:
    for name in ['intake.sqlite','phase1-sandbox.sqlite']:
        if (root/name).exists():
            with sqlite3.connect(root/name) as c, sqlite3.connect(backup/name) as b:c.backup(b)
    for source,target in targets:shutil.copy2(source,target)
    subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',str(root/'registration_app.py'),str(root/'phase1_sandbox.py')],check=True)
    subprocess.run(['systemctl','start','iqs-registration.service'],check=True)
    for _ in range(30):
        try:
            if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
        except requests.RequestException:pass
        time.sleep(.3)
    response=requests.get('http://127.0.0.1:18081/registration/phase1/portal?lang=ha',timeout=5)
    response.raise_for_status()
    assert 'Shafin gwaji na NigeriaG2P' in response.text
    units[0].write_text('[Unit]\nDescription=Escalate overdue fictional Phase 1 grievances\nAfter=iqs-registration.service\n[Service]\nType=oneshot\nWorkingDirectory=/opt/openg2p-lab/registration\nExecStart=/opt/openg2p-lab/registration-venv/bin/python /opt/openg2p-lab/registration/phase1-worker.py\nUMask=0077\n')
    units[1].write_text('[Unit]\nDescription=Check sandbox grievance deadlines every minute\n[Timer]\nOnBootSec=30s\nOnCalendar=*-*-* *:*:00 UTC\nAccuracySec=1s\nPersistent=true\n[Install]\nWantedBy=timers.target\n')
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','enable','--now','iqs-phase1.timer'],check=True)
    subprocess.run(['systemctl','start','iqs-phase1.service'],check=True)
    print('Sandbox deployed; private rollback snapshot:',backup)
except Exception:
    subprocess.run(['systemctl','stop','iqs-phase1.timer'])
    for entry in manifest:
        target=Path(entry['target'])
        if entry['saved']:shutil.copy2(entry['saved'],target)
        elif target.is_file():target.unlink()
    subprocess.run(['systemctl','daemon-reload'])
    subprocess.run(['systemctl','start','iqs-registration.service'])
    raise
