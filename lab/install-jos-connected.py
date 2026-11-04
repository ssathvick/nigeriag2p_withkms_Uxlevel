from pathlib import Path
import shutil,datetime,json,subprocess,sqlite3,requests,time
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration');backup=root/'jos-connected-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
manifest=[]
for source,target in [(src/'registration_app.py',root/'registration_app.py'),(src/'jos_connected.py',root/'jos_connected.py'),(src/'registration-ui/jos-connected.html',root/'templates/jos-connected.html'),(src/'registration-ui/jos-minister.html',root/'templates/jos-minister.html')]:
 saved=backup/str(len(manifest))
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None});shutil.copy2(source,target)
with sqlite3.connect(root/'intake.sqlite') as origin,sqlite3.connect(backup/'intake.sqlite') as dest:origin.backup(dest)
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
try:
 subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',str(root/'registration_app.py'),str(root/'jos_connected.py')],check=True)
 subprocess.run(['systemctl','restart','iqs-registration.service'],check=True)
 for _ in range(20):
  try:
   if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.5)
 assert requests.get('http://127.0.0.1:18081/registration/api/jos-cct',timeout=5).status_code==401
 response=requests.get('http://127.0.0.1:18081/registration/jos-cct',allow_redirects=False,timeout=5);assert response.status_code==302 and 'mode=staff' in response.headers['Location']
 print('Connected Jos staff routes installed; anonymous writes unavailable. Backup:',backup)
except Exception:
 for e in manifest:
  p=Path(e['target'])
  if e['saved']:shutil.copy2(e['saved'],p)
  elif p.exists():p.unlink()
 subprocess.run(['systemctl','restart','iqs-registration.service']);raise
