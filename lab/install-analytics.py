"""Install analytics with a private database backup and rollback for application files."""
from pathlib import Path
import datetime,json,shutil,sqlite3,subprocess,time
import requests
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration')
backup=root/'analytics-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
targets=[(src/name,root/name) for name in ['registration_app.py','knowledge_management.py','platform_analytics.py','analytics_sources.py']]
targets += [(src/'registration-ui'/name,root/'templates'/name) for name in ['analytics.html','base.html','knowledge-library.html','knowledge-admin.html']]
targets += [(src/'knowledge/analytics.js',root/'static/analytics.js')]
manifest=[]
for i,(source,target) in enumerate(targets):
 saved=backup/str(i)
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
(backup/'manifest.json').write_text(json.dumps(manifest))
subprocess.run(['systemctl','stop','iqs-registration.service'],check=True)
try:
 with sqlite3.connect(root/'intake.sqlite') as c,sqlite3.connect(backup/'intake.sqlite') as b:c.backup(b)
 for source,target in targets:shutil.copy2(source,target)
 subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',*[str(root/name) for name in ['registration_app.py','platform_analytics.py','analytics_sources.py']]],check=True)
 subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python',str(src/'setup-analytics-database.py')],check=True)
 subprocess.run(['systemctl','start','iqs-registration.service'],check=True)
 for _ in range(20):
  try:
   if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.3)
 assert requests.get('http://127.0.0.1:18081/registration/health',timeout=5).status_code==200
 service='''[Unit]\nDescription=Nigeria G2P aggregate analytics collection\nAfter=iqs-registration.service\n[Service]\nType=oneshot\nWorkingDirectory=/opt/openg2p-lab/registration\nExecStart=/opt/openg2p-lab/registration-venv/bin/python /opt/openg2p-lab/registration/analytics_sources.py\nUMask=0077\n'''
 timer='''[Unit]\nDescription=Refresh Nigeria G2P analytics every fifteen minutes\n[Timer]\nOnBootSec=2min\nOnUnitActiveSec=15min\nPersistent=true\n[Install]\nWantedBy=timers.target\n'''
 Path('/etc/systemd/system/iqs-analytics.service').write_text(service)
 Path('/etc/systemd/system/iqs-analytics.timer').write_text(timer)
 subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','enable','--now','iqs-analytics.timer'],check=True)
 subprocess.run(['systemctl','start','iqs-analytics.service'],check=True)
 print('Analytics installed and initial collection completed. Private backup:',backup)
except Exception:
 subprocess.run(['systemctl','stop','iqs-analytics.timer'])
 for entry in manifest:
  target=Path(entry['target'])
  if entry['saved']:shutil.copy2(entry['saved'],target)
  elif target.exists():target.unlink()
 subprocess.run(['systemctl','start','iqs-registration.service'])
 raise
