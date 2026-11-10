import datetime as dt,shutil,subprocess
from pathlib import Path
path=Path('/etc/nginx/snippets/iqs-brand.conf');old=path.read_text();new=old.replace('site-shell.js?v=sitewide-20261005-r2','site-shell.js?v=phase1-20261012-readiness')
new=new.replace('knowledge-help.js?v=km12','knowledge-help.js?v=phase1-lang-20261012')
assert 'site-shell.js?v=phase1-20261012-readiness' in new
backup=Path('/opt/openg2p-lab/registration/phase1-backups')/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(mode=0o700,exist_ok=True)
shutil.copy2(path,backup/'iqs-brand.conf');path.write_text(new)
try:
 subprocess.run(['nginx','-t'],check=True)
 subprocess.run(['systemctl','reload','nginx'],check=True)
except Exception:
 path.write_text(old);raise
print('Shared navigation cache version refreshed after syntax validation.')
