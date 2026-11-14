from pathlib import Path
import shutil,subprocess,datetime,os
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');root=Path('/opt/openg2p-lab');branding=root/'branding';snippet=Path('/etc/nginx/snippets/iqs-brand.conf');backup=root/'sitewide-ux-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
targets=[snippet,root/'public-home/index.html',root/'home/index.html',branding/'iqs-brand.js',branding/'site.js',branding/'site.css',branding/'site-shell.js',branding/'site-shell.css']
manifest=[]
for i,target in enumerate(targets):
 if target.exists():shutil.copy2(target,backup/str(i));manifest.append({'target':str(target),'backup':str(backup/str(i))})
 else:manifest.append({'target':str(target),'backup':None})
import json
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2));(backup/'manifest.json').chmod(0o600)
for name in ['site.js','site-shell.js']:shutil.copy2(src/'persona-ui/dist'/name,branding/name)
for name in ['site.css','site-shell.css']:shutil.copy2(src/'sitewide-ui'/name,branding/name)
shutil.copy2(src/'branding/iqs-brand.js',branding/'iqs-brand.js')
for folder in ['public-home','home']:shutil.copy2(src/'sitewide-ui/index.html',root/folder/'index.html')
s=snippet.read_text();old='<script defer src="/iqs-brand/iqs-brand.js"></script></head>';new='<script defer src="/iqs-brand/iqs-brand.js"></script><link rel="stylesheet" href="/iqs-brand/site-shell.css"><script defer src="/iqs-brand/site-shell.js"></script></head>'
if '/site-shell.js' not in s:
 if old not in s:raise RuntimeError('Expected branding injection missing')
 s=s.replace(old,new)
for asset in ['iqs-brand.js','iqs-brand.css','site-shell.js','site-shell.css']:
 s=s.replace('/iqs-brand/'+asset+'?v=sitewide-20261005"','/iqs-brand/'+asset+'?v=sitewide-20261005-r2"').replace('/iqs-brand/'+asset+'"','/iqs-brand/'+asset+'?v=sitewide-20261005-r2"')
snippet.write_text(s)
try:subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
except Exception:
 for entry in manifest:
  if entry['backup']:shutil.copy2(entry['backup'],entry['target'])
 subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True);raise
print('Site-wide UX deployed. Private rollback snapshot:',backup)
