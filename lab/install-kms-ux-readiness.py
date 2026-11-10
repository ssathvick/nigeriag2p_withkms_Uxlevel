"""Deploy only the reviewed KMS and workspace changes, with private rollback files."""
from pathlib import Path
import shutil,hashlib,datetime,json,subprocess,time,sqlite3,requests
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration')
baseline={'knowledge_management.py':'b05eaac55c805f3ad438b3d790b26a67547284df38560a9ac62b2e50d21ae712','local_ai.py':'0d65a68e6f7b3c1f3c2b159c241eecd65aa433e085e6d27fb49f15570a67e7ba'}
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in baseline.items():
 if digest(root/name) not in [h,digest(src/name)]:raise RuntimeError('Unreviewed runtime change: '+name)
targets=[(src/n,root/n) for n in baseline]
targets += [(src/'registration-ui'/n,root/'templates'/n) for n in ['base.html','workspace.html','knowledge-library.html','knowledge-editor.html','knowledge-admin.html','knowledge-article.html']]
targets += [(src/'knowledge/experience.css',root/'static/experience.css'),(src/'persona-ui/dist/workspace.js',root/'static/workspace.js'),(src/'knowledge/help.js',root.parent/'branding/knowledge-help.js')]
backup=root/'kms-ux-backups'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
manifest=[]
for i,(source,target) in enumerate(targets):
 if not source.is_file():raise RuntimeError('Missing source '+str(source))
 saved=backup/str(i)
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None,'sha256':digest(source)})
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
subprocess.run(['systemctl','stop','iqs-registration.service'],check=True)
try:
 with sqlite3.connect(root/'intake.sqlite') as c,sqlite3.connect(backup/'intake.sqlite') as b:c.backup(b)
 for source,target in targets:shutil.copy2(source,target)
 subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',*[str(root/n) for n in baseline]],check=True)
 subprocess.run(['systemctl','start','iqs-registration.service'],check=True)
 for _ in range(30):
  try:
   if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.3)
 for path in ['/health','/knowledge','/api/knowledge','/workspace?demo=1']:
  requests.get('http://127.0.0.1:18081/registration'+path,timeout=10).raise_for_status()
 print('KMS and UX deployment healthy; private rollback backup retained.')
except Exception:
 for item in manifest:
  if item['saved']:shutil.copy2(item['saved'],item['target'])
  elif Path(item['target']).exists():Path(item['target']).unlink()
 subprocess.run(['systemctl','restart','iqs-registration.service']);raise
