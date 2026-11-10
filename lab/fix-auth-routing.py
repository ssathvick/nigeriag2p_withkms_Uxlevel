from pathlib import Path
import datetime,shutil,subprocess,json
src=Path(__file__).resolve().parent
backup=Path('/opt/openg2p-lab/backups')/('auth-routing-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
p=Path('/etc/nginx/conf.d/iqs-dual-domain.conf');shutil.copy2(p,backup/p.name)
old=p.read_text();needle=' openg2p-superset $iqs_native_args_23_1;'
assert needle in old
new=old.replace(needle,needle+'\n staff-portal $iqs_native_args_23_1;')
p.write_text(new)
try:subprocess.run(['nginx','-t'],check=True)
except Exception:p.write_text(old);raise
p=src/'dual-domain/nginx-alias.conf';s=p.read_text();p.write_text(s.replace(needle,needle+'\n staff-portal $iqs_native_args_23_1;'))
target=Path('/opt/openg2p-lab/branding/dashboard-landing.js');shutil.copy2(target,backup/target.name);shutil.copy2(src/'persona-ui/src/dashboard-landing.js',target)
subprocess.run(['systemctl','reload','nginx'],check=True)
print(json.dumps({'backup':str(backup),'changes':['Preserve requested service routes','Match staff-portal authorization callback to token exchange']}))
