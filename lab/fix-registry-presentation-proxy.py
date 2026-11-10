"""Request explicit identity encoding so HTML presentation filters can run."""
from pathlib import Path
import datetime,json,shutil,subprocess,time
import requests
backup=Path('/opt/openg2p-lab/registration/dashboard-backups')/('identity-encoding-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,mode=0o700)
paths=[Path('/etc/nginx/sites-enabled/'+n).resolve() for n in ['iqs-public','openg2p-lab']]
manifest=[]
for i,p in enumerate(paths):
 saved=backup/str(i);shutil.copy2(p,saved)
 manifest.append({'target':str(p),'saved':str(saved)})
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
try:
 for p in paths:
  p.write_text(p.read_text().replace('proxy_set_header Accept-Encoding "";', 'proxy_set_header Accept-Encoding "identity";'))
 subprocess.run(['nginx','-t'],check=True)
 subprocess.run(['systemctl','reload','nginx'],check=True)
 for attempt in range(8):
  r=requests.get('http://127.0.0.1:18080/en',headers={'Host':'g2p-register.wverve.in','Connection':'close'},timeout=20)
  if r.status_code==200 and 'service-insights.js' in r.text:break
  time.sleep(.4)
 else:raise RuntimeError('Presentation assets not delivered')
 print('Registry presentation injection verified. Backup:',backup)
except Exception:
 for entry in manifest:shutil.copy2(entry['saved'],entry['target'])
 subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'])
 raise
