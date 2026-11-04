"""Publish isolated synthetic pilot and its service link, with rollback."""
from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,requests,time,re
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');base=Path('/opt/openg2p-lab')
backup=base/'registration/jos-cct-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
version=hashlib.sha256((src/'persona-ui/dist/jos-cct.js').read_bytes()+(src/'persona-ui/dist/jos-cct.css').read_bytes()).hexdigest()[:12]
manifest=[]
def save(p):
 saved=backup/str(len(manifest))
 if p.exists():shutil.copy2(p,saved)
 manifest.append({'target':str(p),'saved':str(saved) if saved.exists() else None})
try:
 config=Path('/etc/nginx/sites-available/iqs-public');save(config);text=config.read_text()
 if 'location ^~ /jos-cct/' not in text:
  anchor=' root /opt/openg2p-lab/public-home;';assert text.count(anchor)==1
  text=text.replace(anchor,anchor+'\n location = /jos-cct { return 308 https://nigeriag2p.com/jos-cct/; }\n location ^~ /jos-cct/ {\n  sub_filter \'</head>\' \'</head>\';\n  add_header Cache-Control "no-cache";\n  try_files $uri $uri/ =404;\n }')
  config.write_text(text)
 for folder in ['public-home','home']:
  target=base/folder/'jos-cct';target.mkdir(exist_ok=True)
  for name in ['index.html','brief.html','jos-cct.js','jos-cct.css']:
   origin=src/('jos-cct' if name.endswith('.html') else 'persona-ui/dist')/name;dest=target/name;save(dest)
   dest.write_text(origin.read_text().replace('VERSION',version)) if name=='index.html' else shutil.copy2(origin,dest)
   dest.chmod(0o644)
  home=base/folder/'index.html';save(home);home.write_text(re.sub(r'site\.js\?v=[^"\s]+','site.js?v=jos-'+version,home.read_text()))
 target=base/'branding/site.js';save(target);shutil.copy2(src/'persona-ui/dist/site.js',target)
 (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
 subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
 time.sleep(1)
 for asset in ['','brief.html','jos-cct.js','jos-cct.css']:
  r=requests.get('http://127.0.0.1:18080/jos-cct/'+asset,headers={'Host':'nigeriag2p.com'},timeout=15);assert r.status_code==200,(asset,r.status_code);assert not r.headers.get('Set-Cookie')
  if asset=='':assert 'site-shell.js' not in r.text and 'jos-root' in r.text
 assert requests.get('http://127.0.0.1:18081/registration/api/analytics',timeout=5).status_code==401
 print('Jos synthetic pilot published. Rollback:',backup/'manifest.json')
except Exception:
 for e in reversed(manifest):
  p=Path(e['target'])
  if e['saved']:shutil.copy2(e['saved'],p)
  elif p.exists():p.unlink()
 subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx']);raise
