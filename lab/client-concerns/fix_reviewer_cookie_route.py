"""Match the public edge cookie scope on the locally resolved staff IAM route."""
from pathlib import Path
import datetime,subprocess,shutil,os
MAP='''# Local HTTPS staff-IAM callback must use the same cookie domain as the public edge.
map $host $nsipa_staff_cookie_domain {
    default nigeriag2p.com;
    g2p-staff-iam.wverve.in wverve.in;
}
'''
def main():
 os.umask(0o077)
 target=Path('/etc/nginx/sites-available/openg2p-lab')
 mapping=Path('/etc/nginx/conf.d/nsipa-staff-cookie-domain.conf')
 before=target.read_text();oldmap=mapping.read_text() if mapping.exists() else None
 directive='    proxy_cookie_domain nigeriag2p.com $nsipa_staff_cookie_domain;\n'
 if directive in before and oldmap==MAP:print('Cookie route already corrected');return
 assert 'g2p-staff-iam.wverve.in' in before
 anchor='    ssl_certificate /opt/openg2p-lab/tls/server.crt;'
 assert before.count(anchor)==1
 after=before if directive in before else before.replace(anchor,directive+anchor,1)
 backup=Path('/opt/openg2p-lab/backups')/('reviewer-cookie-route-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
 backup.mkdir();shutil.copy2(target,backup/target.name)
 if mapping.exists():shutil.copy2(mapping,backup/mapping.name)
 try:
  mapping.write_text(MAP);target.write_text(after)
  subprocess.run(['nginx','-t'],check=True,capture_output=True)
  subprocess.run(['systemctl','reload','nginx'],check=True)
 except Exception:
  target.write_text(before)
  if oldmap is None:mapping.unlink(missing_ok=True)
  else:mapping.write_text(oldmap)
  raise
 print('Validated and reloaded Nginx. Backup:',backup)
if __name__=='__main__':main()
