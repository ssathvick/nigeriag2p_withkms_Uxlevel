from pathlib import Path
import shutil,datetime,subprocess
backup=Path('/opt/openg2p-lab/backups')/('auth-cookies-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
base=Path('/etc/nginx/sites-available/iqs-wverve');alias=Path('/etc/nginx/conf.d/iqs-dual-domain.conf');old={p:p.read_text() for p in [base,alias]}
for p in old:shutil.copy2(p,backup/p.name)
s=old[base];needle=' server_name g2p-minio-api.wverve.in';idx=s.index(needle);end=s.index('\n',idx);s=s[:end]+ '\n proxy_cookie_domain nigeriag2p.com wverve.in;'+s[end:];base.write_text(s)
needle=" sub_filter_once off;";s=old[alias];assert needle in s;s=s.replace(needle,' proxy_cookie_domain wverve.in nigeriag2p.com;\n'+needle);alias.write_text(s)
try:subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
except Exception:
 for p,content in old.items():p.write_text(content)
 raise
p=Path(__file__).parent/'dual-domain/nginx-alias.conf';p.write_text(p.read_text().replace(needle,' proxy_cookie_domain wverve.in nigeriag2p.com;\n'+needle))
print('Cookie domains now follow the requested host family. Backup: '+str(backup))
