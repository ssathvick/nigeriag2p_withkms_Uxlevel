"""Install the reversible React workspace update without recreating OIDC clients or fixtures."""
from pathlib import Path
import datetime,shutil,sqlite3,subprocess
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab/registration')
backup=root/'persona-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
for name in ['registration_app.py','registration_workspaces.py','nigeria_geography.py','nigeria-geography.json']:
 if (root/name).exists():shutil.copy2(root/name,backup/name)
shutil.copytree(root/'templates',backup/'templates');shutil.copytree(root/'static',backup/'static')
with sqlite3.connect(root/'intake.sqlite') as source,sqlite3.connect(backup/'intake.sqlite') as target:source.backup(target)
homes=[Path('/opt/openg2p-lab/public-home/index.html'),Path('/opt/openg2p-lab/home/index.html')]
for i,home in enumerate(homes):
 if home.exists():shutil.copy2(home,backup/f'home-{i}.html')
for name in ['registration_app.py','registration_workspaces.py','nigeria_geography.py','nigeria-geography.json']:shutil.copy2(src/name,root/name)
for name in ['profile.html','geography.html']:shutil.copy2(src/'registration-ui'/name,root/'templates'/name)
shutil.copy2(src/'registration-ui/geo-form.js',root/'static/geo-form.js')
shutil.copy2(src/'registration-ui/workspace.html',root/'templates/workspace.html')
shutil.copy2(src/'registration-ui/workspace.css',root/'static/workspace.css')
shutil.copy2(src/'persona-ui/dist/workspace.js',root/'static/workspace.js')
base=root/'templates/base.html';t=base.read_text()
if '/workspace' not in t:t=t.replace('<nav>','<nav><a href="{{prefix}}/workspace{% if not user %}?demo=1{% endif %}">Persona workspace</a>')
base.write_text(t)
cards='<a class="card" href="https://g2p.wverve.in/registration/workspace?demo=1"><h2>Client persona walkthrough</h2><p>Explore registration, verification, supervision and citizen support with fictional records.</p></a><a class="card" href="https://g2p.wverve.in/registration/workspace"><h2>My persona workspace</h2><p>Sign in to view household registration and staff review in the new workspace.</p></a>'
for home in homes:
 if home.exists():
  html=home.read_text()
  if 'Client persona walkthrough' not in html:home.write_text(html.replace('<div class="grid">','<div class="grid">'+cards))
subprocess.run([str(root.parent/'registration-venv/bin/python'),'-m','py_compile',str(root/'registration_app.py'),str(root/'registration_workspaces.py')],check=True)
subprocess.run(['systemctl','restart','iqs-registration.service'],check=True)
print('Persona workspace installed; private rollback snapshot retained. Existing identity clients and programme data preserved.')
