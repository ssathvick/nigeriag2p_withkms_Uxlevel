from pathlib import Path
import shutil,requests
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app')
for name in ['public-home','home']:
 p=Path('/opt/openg2p-lab')/name/'field-preview';p.mkdir(exist_ok=True)
 for f in ['index.html','preview.css','preview.js','sw.js','manifest.webmanifest','nsipa-logo.png','apple-touch-icon.png','icon-512.png','nsipa-field-demo.xlsx','nsipa-field-demo.xml']:
  shutil.copy2(src/f,p/f);(p/f).chmod(0o644)
r=requests.get('http://127.0.0.1:18080/field-preview/',headers={'Host':'nigeriag2p.com'},timeout=5);print('Preview HTTP',r.status_code);assert r.status_code==200
