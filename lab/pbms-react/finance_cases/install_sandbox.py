"""Install scoped Bridge views, the sandbox case register and the PBMS navigation link."""
import datetime,os,pathlib,secrets,shutil,subprocess,sys,time
import requests
from psycopg2 import sql
from psycopg2.extensions import make_dsn
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as platform
src=pathlib.Path(__file__).resolve().parent;react=src.parent;root=pathlib.Path('/opt/openg2p-lab/pbms-react')
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-finance-cases'
backup=root/'backups'/stamp;backup.mkdir(mode=0o700)
role='pbms_finance_evidence_reader';env=root/'adapter/finance-cases.env'
previous=(root/'current').resolve();release=root/'releases'/stamp
if env.exists():password=env.read_text().split('password=')[1].split()[0].strip('"')
else:password=secrets.token_hex(32)
with platform.pg('bridge_db') as con:
 with con.cursor() as q:
  q.execute((src/'evidence.sql').read_text());q.execute('select 1 from pg_roles where rolname=%s',(role,))
  if not q.fetchone():q.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD %s').format(sql.Identifier(role)),(password,))
  q.execute(sql.SQL('GRANT USAGE ON SCHEMA pbms_finance TO {}').format(sql.Identifier(role)))
  q.execute(sql.SQL('GRANT SELECT ON pbms_finance.instructions,pbms_finance.entries TO {}').format(sql.Identifier(role)))
  q.execute("select has_table_privilege(%s,'public.account_statement_lobs','SELECT')",(role,));assert not q.fetchone()[0]
dsn=make_dsn(host=platform.svc('commons-postgresql')[7:],dbname='bridge_db',user=role,password=password)
def write(p,b,perms=0o644):
 f=p.with_name(p.name+'.stage');fd=os.open(f,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,perms)
 with os.fdopen(fd,'wb') as out:out.write(b)
 f.chmod(perms);f.replace(p)
write(env,('FINANCE_EVIDENCE_DSN="'+dsn+'"\n').encode(),0o600)
drop=pathlib.Path('/etc/systemd/system/pbms-react-api.service.d/finance-cases.conf')
drop.parent.mkdir(exist_ok=True)
target=root/'adapter/workflow_api.py';shutil.copy2(target,backup/'workflow_api.py')
package=root/'adapter/finance_cases';package.mkdir(exist_ok=True)
if (package/'register.py').exists():shutil.copytree(package,backup/'finance_cases')
if drop.exists():shutil.copy2(drop,backup/drop.name)
shutil.copytree(previous,release)
for name in ('app.js','app.css'):
 shutil.copy2(react/'dist'/name,release/name)
def switch(path):
 tmp=root/'current-finance-next';tmp.symlink_to(path);tmp.replace(root/'current')
def cmd(*a):subprocess.run(a,check=True,stdout=subprocess.DEVNULL)
try:
 # Preserve adapter changes unrelated to the new routes.
 hook=b'from finance_cases.register import install as install_finance_cases\ninstall_finance_cases(app, User, Problem)\n'
 old=target.read_bytes()
 if hook not in old:write(target,old.rstrip()+b'\n\n'+hook)
 for n in ['register.py','register.html']:write(package/n,(src/n).read_bytes())
 write(drop,('[Service]\nStateDirectory=pbms-finance\nStateDirectoryMode=0700\nEnvironmentFile='+str(env)+'\n').encode())
 cmd('systemctl','daemon-reload');cmd('systemctl','restart','pbms-react-api')
 for tick in range(20):
  try:
   if requests.get('http://127.0.0.1:18112/pbms-ui-api/finance-register',timeout=2).status_code==200:break
  except requests.RequestException:pass
  time.sleep(.5)
 else:raise RuntimeError('New register did not pass health check')
 switch(release)
except BaseException:
 write(target,(backup/'workflow_api.py').read_bytes())
 if (backup/'finance_cases').exists():shutil.copytree(backup/'finance_cases',package,dirs_exist_ok=True)
 if (backup/drop.name).exists():write(drop,(backup/drop.name).read_bytes())
 else:drop.unlink(missing_ok=True)
 cmd('systemctl','daemon-reload');cmd('systemctl','restart','pbms-react-api');raise
print('Installed',stamp,'previous',previous.name)
