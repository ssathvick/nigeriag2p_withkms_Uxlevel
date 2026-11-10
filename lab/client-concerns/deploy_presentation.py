from pathlib import Path
import shutil,subprocess
src=Path(__file__).parent.parent;root=Path('/opt/openg2p-lab');backup=Path((src/'client-concerns/backup-location.txt').read_text())
for name in ['registration_app.py','registration_workspaces.py']:shutil.copy2(src/name,root/'registration'/name)
for name in ['workspace.js','dashboard.js']:shutil.copy2(src/'persona-ui/dist'/name,root/'registration/static'/name)
for name in ['site.js','site-shell.js','service-insights.js']:shutil.copy2(src/'persona-ui/dist'/name,root/'branding'/name)
for name in ['registry-presentation.js','registry-presentation.css']:shutil.copy2(src/'client-concerns'/name,root/'branding'/name)
snippet=Path('/etc/nginx/snippets/iqs-brand.conf');shutil.copy2(snippet,backup/'iqs-brand.conf')
s=snippet.read_text()
if 'registry-presentation.js' not in s:s=s.replace('</head>\';','<link rel="stylesheet" href="/iqs-brand/registry-presentation.css"><script src="/iqs-brand/registry-presentation.js"></script></head>\';')
snippet.write_text(s)
subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True);subprocess.run(['systemctl','restart','iqs-registration'],check=True)
print('Updated native registry cards, provenance panel, shared names and registration rework history.')
