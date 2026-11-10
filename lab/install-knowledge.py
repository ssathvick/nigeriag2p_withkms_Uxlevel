from pathlib import Path
import sqlite3,shutil,datetime,subprocess,json
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration');brand=root.parent/'branding';snippet=Path('/etc/nginx/snippets/iqs-brand.conf');backup=root/'knowledge-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
targets=[(src/'local_ai.py',root/'local_ai.py'),(src/'ai/local-ai.js',root/'static/local-ai.js'),(src/'registration_app.py',root/'registration_app.py'),(src/'knowledge_management.py',root/'knowledge_management.py'),(src/'knowledge-seed.json',root/'knowledge-seed.json'),(src/'knowledge/help.js',brand/'knowledge-help.js'),(src/'knowledge/context.js',brand/'knowledge-context.js'),(src/'persona-ui/dist/workspace.js',root/'static/workspace.js'),(src/'knowledge/help.css',brand/'knowledge-help.css')]+[(src/'registration-ui'/name,root/'templates'/name) for name in ['local-ai.html','knowledge-library.html','knowledge-admin.html','knowledge-editor.html','knowledge-revision.html','profile.html','review.html','staff.html','geography.html','home.html']]
manifest=[]
for i,(source,target) in enumerate(targets):
 saved=backup/str(i)
 if target.exists():shutil.copy2(target,saved)
 manifest.append({'target':str(target),'saved':str(saved) if saved.exists() else None})
shutil.copy2(snippet,backup/'nginx-snippet');(backup/'manifest.json').write_text(json.dumps(manifest))
subprocess.run(['systemctl','stop','iqs-registration.service'],check=True)
try:
 with sqlite3.connect(root/'intake.sqlite') as c,sqlite3.connect(backup/'intake.sqlite') as b:c.backup(b)
 for source,target in targets:shutil.copy2(source,target)
 subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','-m','py_compile',str(root/'registration_app.py'),str(root/'knowledge_management.py')],check=True)
 s=snippet.read_text()
 if 'location = /iqs-brand/knowledge' not in s:s='location = /iqs-brand/knowledge { proxy_pass http://127.0.0.1:18081/registration/api/knowledge; proxy_set_header Host g2p.wverve.in; proxy_set_header Cookie \"\"; proxy_hide_header Set-Cookie; }\n'+s
 if '/knowledge-help.js' not in s:s=s.replace('</head>\';', '<link rel="stylesheet" href="/iqs-brand/knowledge-help.css?v=km5"><script defer src="/iqs-brand/knowledge-help.js?v=km5"></script></head>\';')
 s=s.replace('v=km1','v=km5').replace('v=km2','v=km5').replace('v=km3','v=km5').replace('v=km4','v=km5')
 if '/knowledge-context.js' not in s:s=s.replace('<script defer src="/iqs-brand/knowledge-help.js', '<script defer src="/iqs-brand/knowledge-context.js?v=km6"></script><script defer src="/iqs-brand/knowledge-help.js')
 import re
 s=re.sub(r'v=km[0-9]+','v=km12',s)
 snippet.write_text(s);subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','start','iqs-registration.service'],check=True)
 import requests,time
 for _ in range(20):
  try:
   if requests.get('http://127.0.0.1:18081/registration/health',timeout=2).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.25)
 assert requests.get('http://127.0.0.1:18081/registration/health',timeout=10).status_code==200
 subprocess.run(['systemctl','reload','nginx'],check=True)
 print('Knowledge management installed; private source/database backup retained.')
except Exception:
 for entry in manifest:
  if entry['saved']:shutil.copy2(entry['saved'],entry['target'])
 shutil.copy2(backup/'nginx-snippet',snippet);subprocess.run(['systemctl','start','iqs-registration.service']);raise

