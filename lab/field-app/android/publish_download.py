from pathlib import Path
import shutil,requests
base=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android')
for home in ['public-home','home']:
 target=Path('/opt/openg2p-lab')/home/'field-preview'/'android'
 target.mkdir(parents=True,exist_ok=True)
 shutil.copy2(base/'test-instructions.html',target/'index.html')
 shutil.copy2(base/'build/nigeria-g2p-field-demo.apk',target/'nigeria-g2p-field-demo.apk')
 shutil.copy2(base/'build/nigeria-g2p-field-demo.apk',target/'nigeria-g2p-field-demo-v0.6.apk')
 for p in target.iterdir():p.chmod(0o644)
for name in ['index.html','nigeria-g2p-field-demo.apk']:
 r=requests.get('http://127.0.0.1:18080/field-preview/android/'+name,headers={'Host':'g2p.wverve.in'},timeout=10);r.raise_for_status();print(name,r.status_code,len(r.content),r.headers.get('Content-Type'))
