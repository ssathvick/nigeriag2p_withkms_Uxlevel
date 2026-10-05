"""Create a private logical database and file-volume backup inside WSL."""
import subprocess,json,base64,os,pathlib,datetime,tarfile,sqlite3
root=pathlib.Path('/opt/openg2p-lab/backups')/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
root.mkdir(parents=True,mode=0o700)
for service in ['commons-postgresql','pbms-postgresql','registry-postgresql','example-bank-postgresql','portal-backend-postgresql']:
 secret=json.loads(subprocess.check_output(['kubectl','get','secret',service,'-n','nigeria','-o','json']))
 ip=subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
 env=os.environ|{'PGPASSWORD':base64.b64decode(secret['data']['postgres-password']).decode()}
 with (root/(service+'.sql')).open('w') as output:
  subprocess.run(['kubectl','-n','nigeria','exec','svc/'+service,'--','env','PGPASSWORD='+env['PGPASSWORD'],'pg_dumpall','-U','postgres'],stdout=output,check=True)
 with (root/(service+'.sql')).open() as f:pass
 os.chmod(root/(service+'.sql'),0o600)
with (root/'kubernetes.yaml').open('wb') as f:
 subprocess.run(['kubectl','get','deploy,sts,svc,cm,secret,pvc,virtualservice,gateway','-n','nigeria','-o','yaml'],stdout=f,check=True)
os.chmod(root/'kubernetes.yaml',0o600)
# Snapshot the intake database with SQLite's backup API, including committed WAL data.
intake=pathlib.Path('/opt/openg2p-lab/registration/intake.sqlite')
if intake.exists():
 with sqlite3.connect(intake) as source,sqlite3.connect(root/'registration-intake.sqlite') as destination:source.backup(destination)
 os.chmod(root/'registration-intake.sqlite',0o600)
def archive_filter(info):
 if any(info.name.endswith(s) for s in ['/intake.sqlite','/intake.sqlite-wal','/intake.sqlite-shm']):return None
 return info
# Databases above are transaction-consistent logical backups; file volumes are copied online.
pvs=json.loads(subprocess.check_output(['kubectl','get','pv','-o','json']))['items']
with tarfile.open(root/'files-and-config.tar.gz','w:gz') as tar:
 for pv in pvs:
  claim=pv['spec'].get('claimRef',{})
  if claim.get('namespace')!='nigeria' or 'postgresql' in claim.get('name',''):continue
  path=pv['spec'].get('hostPath',{}).get('path')
  if path and pathlib.Path(path).exists():tar.add(path,arcname='volumes/'+claim['name'])
 for path in ['credentials.yaml','tls','charts','branding','branding-backup','home','baseline','start-lab-host.sh','wait-lab-ready.py','commons-base.yaml','commons-services.yaml','pbms.yaml','registry.yaml','register.yaml','spar.yaml','bridge.yaml','beneficiary.yaml','portal-backend.yaml','nigeria-fixtures.json']:
  full=pathlib.Path('/opt/openg2p-lab')/path
  if full.exists():tar.add(full,arcname='configuration/'+path)
 for path in ['/etc/nginx/sites-available/openg2p-lab','/etc/nginx/sites-available/iqs-public','/etc/nginx/snippets/iqs-brand.conf','/etc/cloudflared','/root/.cloudflared','/opt/openg2p-lab/public-home','/opt/openg2p-lab/public-hostnames.json','/opt/openg2p-lab/public-domain-backup','/opt/openg2p-lab/public-verification.json','/opt/openg2p-lab/registration','/opt/openg2p-lab/household-adapter','/etc/systemd/system/iqs-registration.service','/etc/systemd/system/iqs-registration-sync.service','/etc/systemd/system/iqs-registration-sync.timer']:
  if pathlib.Path(path).exists():tar.add(path,arcname='configuration'+path,filter=archive_filter)
os.chmod(root/'files-and-config.tar.gz',0o600)
print('Private backup created:',root)
