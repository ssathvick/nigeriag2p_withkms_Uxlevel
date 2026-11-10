"""Publish only the reviewed static public data package; private APIs are untouched."""
from pathlib import Path
import json,datetime,hashlib,shutil,subprocess
import requests
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');base=Path('/opt/openg2p-lab')
subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python',str(src/'test-territory-data.py')],check=True)
backup=base/'registration/territory-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
version=hashlib.sha256((src/'persona-ui/dist/territories.js').read_bytes()+(src/'persona-ui/dist/territories.css').read_bytes()+(src/'territory-data/public/data.json').read_bytes()).hexdigest()[:12]
manifest=[]
try:
 config=Path('/etc/nginx/sites-available/iqs-public');saved=backup/'nginx-public';shutil.copy2(config,saved);manifest.append({'target':str(config),'saved':str(saved)})
 content=config.read_text()
 if '# Public territorial atlas: standalone presentation' not in content:
  anchor=' root /opt/openg2p-lab/public-home;'
  assert content.count(anchor)==1
  content=content.replace(anchor,anchor+'''\n # Public territorial atlas: standalone presentation, no authenticated app widgets.
 location ^~ /territories/ {
  sub_filter '</head>' '</head>';
  add_header Cache-Control "no-cache";
  try_files $uri $uri/ =404;
 }''')
  config.write_text(content)
 if 'location = /territories {' not in content:
  content=content.replace(' # Public territorial atlas: standalone presentation', ' location = /territories { return 308 https://g2p.wverve.in/territories/; }\n # Public territorial atlas: standalone presentation')
  config.write_text(content)
 for folder in ['public-home','home']:
  target=base/folder/'territories';target.mkdir(exist_ok=True)
  copies=[(src/'territory-data/public'/n,n) for n in ['data.json','states.geojson','lgas.geojson','measures.csv']]+[(src/'persona-ui/dist'/n,n) for n in ['territories.js','territories.css']]+[(src/'territory-data/index.html','index.html')]
  for origin,name in copies:
   dest=target/name;saved=backup/str(len(manifest))
   if dest.exists():shutil.copy2(dest,saved)
   manifest.append({'target':str(dest),'saved':str(saved) if saved.exists() else None})
   if name=='index.html':dest.write_text(origin.read_text().replace('VERSION',version))
   else:shutil.copy2(origin,dest)
   dest.chmod(0o644)
 (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
 subprocess.run(['nginx','-t'],check=True)
 subprocess.run(['systemctl','reload','nginx'],check=True)
 for name in ['','data.json','states.geojson','lgas.geojson','measures.csv','territories.js','territories.css']:
  r=requests.get('http://127.0.0.1:18080/territories/'+name,headers={'Host':'g2p.wverve.in'},timeout=15)
  assert r.status_code==200,(name,r.status_code)
  assert not r.headers.get('Set-Cookie'),name
  if name=='data.json':assert len(r.json()['districts'])==109
 assert requests.get('http://127.0.0.1:18081/registration/api/analytics',timeout=5).status_code==401
 print('Public atlas deployed without authentication. Private analytics still require login. Rollback:',backup/'manifest.json')
except Exception:
 for entry in manifest:
  dest=Path(entry['target'])
  if entry['saved']:shutil.copy2(entry['saved'],dest)
  elif dest.exists():dest.unlink()
 subprocess.run(['nginx','-t'],check=True)
 subprocess.run(['systemctl','reload','nginx'])
 raise
