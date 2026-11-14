"""Cut over native registry entry points after a verified, lossless historical import."""
raise SystemExit('Retired: use integrate_native_registry_accounts.py and restore_native_registry_authority.py. The native Master Registry owns this workflow.')
import datetime,json,os,py_compile,shutil,subprocess
from pathlib import Path
import requests,yaml
from psycopg2.extras import Json,RealDictCursor
from test_mbr_db_connection import connect
from mbr_native_migration import migrate

SOURCE=Path(__file__).parent;ROOT=Path('/opt/openg2p-lab/registration')
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup=ROOT/'mbr-integration-backups'/stamp
backup.mkdir(parents=True,mode=0o700)
manifest=[]
def change(path,text):
 path=Path(path);saved=backup/str(len(manifest))
 if path.exists():shutil.copy2(path,saved)
 manifest.append({'path':str(path),'saved':str(saved) if saved.exists() else None})
 path.write_text(text)
def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True)
def kube(*args):return run('kubectl','-n','nigeria',*args).stdout.strip()

# Capture another full recovery point immediately before live cutover.
snapshot=run('/opt/openg2p-lab/registration-venv/bin/python',str(SOURCE/'snapshot_mbr_migration.py'))
(backup/'snapshot.json').write_text(snapshot.stdout)

# Ship the native adapters before restarting the existing registration service.
run('/opt/openg2p-lab/registration-venv/bin/python',str(SOURCE/'deploy-mbr-workflow.py'))
live=(ROOT/'registration_app.py').read_text()
live=live.replace("'mbr':request.args.get('mbr')=='1',","'mbr_return':g.session.get('mbr_return'),'mbr':request.args.get('mbr')=='1',") if "'mbr_return':g.session.get('mbr_return')" not in live else live
live=live.replace("if flow.get('mbr'):return redirect(PREFIX+'/mbr')", "if flow.get('mbr'):return redirect(flow.get('mbr_return') if str(flow.get('mbr_return') or '').startswith(PREFIX+'/mbr?') else PREFIX+'/mbr')")
candidate=backup/'registration_app.new.py';candidate.write_text(live);py_compile.compile(str(candidate),doraise=True)
change(ROOT/'registration_app.py',live)
run('systemctl','restart','iqs-registration')

# Add MBR roles to the explicitly established native demo identities; no password changes.
kc='http://'+kube('get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}')
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
t=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);t.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+t.json()['access_token'];realm=kc+'/admin/realms/staff'
rr=s.get(realm+'/users',params={'max':1000},timeout=20);rr.raise_for_status();users=rr.json()
rolemap={'admin':'mbr-admin','nsipa-demo-intake':'mbr-officer','nsipa-demo-reviewer-one':'mbr-level1','nsipa-demo-reviewer-two':'mbr-level2'}
roles_added=[];aliases={}
for user in users:
 name=' '.join(x for x in [user.get('firstName'),user.get('lastName')] if x)
 for alias in [user['id'],user['username'],user.get('email'),name]:
  if alias:aliases.setdefault(alias,set()).add(user['id'])
 if user['username'] in rolemap:
  role=rolemap[user['username']]
  assigned=s.get(realm+'/users/'+user['id']+'/role-mappings/realm',timeout=20);assigned.raise_for_status()
  others=[x for x in assigned.json() if x['name'].startswith('mbr-') and x['name']!=role]
  if others:raise RuntimeError('Conflicting role on existing identity '+user['username'])
  role_data=s.get(realm+'/roles/'+role,timeout=20);role_data.raise_for_status()
  if not any(x['name']==role for x in assigned.json()):
   s.post(realm+'/users/'+user['id']+'/role-mappings/realm',json=[role_data.json()],timeout=20).raise_for_status();roles_added.append({'id':user['id'],'role':role})
with connect() as c:
 with c.cursor() as cur:
  for alias,ids in aliases.items():
   if len(ids)!=1:continue
   actor=next(iter(ids));cur.execute('SELECT actor_id FROM g2p_mbr_actor_alias WHERE alias=%s',(alias,));old=cur.fetchone()
   if old and old[0]!=actor:raise RuntimeError('Ambiguous original actor identity; refusing overwrite')
   cur.execute('INSERT INTO g2p_mbr_actor_alias(alias,actor_id) VALUES(%s,%s) ON CONFLICT DO NOTHING',(alias,actor))
(backup/'role-grants.json').write_text(json.dumps(roles_added))

# The import refuses source drift and reconciles every historical request before routing changes.
report=migrate(apply=True,guards=True)
(backup/'migration-report.json').write_text(json.dumps(report,indent=2));(backup/'migration-report.json').chmod(0o600)
if report['native_records']<32 or not report['source_tables_unchanged']:raise RuntimeError('Migration failed reconciliation')

map_text='''# Integrated registry workflow; native_view=1 is a deliberate read-only/configuration escape.
map "$host:$uri:$arg_native_view" $mbr_registry_redirect {
 default "";
 "~^g2p-register\\.wverve\\.in:(?:/|/en/?|/en/(?:intake-form|change-request|tasks)(?:/.*)?):$" "https://g2p.wverve.in/registration/mbr/legacy?path=$uri";
 "~^g2p-awe\\.wverve\\.in:/(?:requests|tasks)/[0-9a-fA-F-]{36}:$" "https://g2p.wverve.in/registration/mbr/legacy?path=/awe$uri";
}
'''
try:
 change('/etc/nginx/conf.d/mbr-registry-routing.conf',map_text)
 for filename in ['iqs-wverve','openg2p-lab']:
  path=(Path('/etc/nginx/sites-enabled')/filename).resolve();text=path.read_text();lines=text.splitlines();output=[]
  for line in lines:
   output.append(line)
   if line.lstrip().startswith('server_name ') and 'g2p-register.wverve.in' in line:
    output.append(' if ($mbr_registry_redirect != "") { return 302 $mbr_registry_redirect; } # MBR workflow owner')
  # Keep deployment reruns idempotent.
  result='\n'.join(output)+'\n'
  result=result.replace(' if ($mbr_registry_redirect != "") { return 302 $mbr_registry_redirect; } # MBR workflow owner\n if ($mbr_registry_redirect != "") { return 302 $mbr_registry_redirect; } # MBR workflow owner\n',' if ($mbr_registry_redirect != "") { return 302 $mbr_registry_redirect; } # MBR workflow owner\n')
  change(path,result)
 run('nginx','-t');run('systemctl','reload','nginx')
 import time
 for attempt in range(12):
  check=requests.get('http://127.0.0.1:18080/en',headers={'Host':'g2p-register.wverve.in','Connection':'close'},allow_redirects=False,timeout=15)
  if check.status_code==302 and '/registration/mbr/legacy' in check.headers.get('Location',''):break
  time.sleep(.25)
 else:raise RuntimeError('Native entry point did not route to MBR: '+str(check.status_code)+' '+check.headers.get('Location',''))
 # Future native/ODK ingests also enter the same queue; no-op runs avoid locking tables.
 service='''[Unit]
Description=Import native registry artifacts into the integrated MBR workflow
After=iqs-registration.service
[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/openg2p-lab/registration
ExecStart=/opt/openg2p-lab/registration-venv/bin/python /opt/openg2p-lab/registration/mbr_native_migration.py --apply --guards --if-new --report /opt/openg2p-lab/registration/mbr-native-latest.json
'''
 timer='''[Unit]
Description=Reconcile newly ingested native registry artifacts
[Timer]
OnBootSec=45s
OnUnitActiveSec=60s
Unit=iqs-mbr-native-import.service
[Install]
WantedBy=timers.target
'''
 change('/etc/systemd/system/iqs-mbr-native-import.service',service);change('/etc/systemd/system/iqs-mbr-native-import.timer',timer)
 run('systemctl','daemon-reload');run('systemctl','enable','--now','iqs-mbr-native-import.timer')
 (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps({'status':'integrated','backup':str(backup),'migration':{k:v for k,v in report.items() if k not in ['links','source_counts','source_hashes']},'existing_native_identities_added':[x['role'] for x in roles_added]}))
except Exception:
 for entry in reversed(manifest):
  path=Path(entry['path'])
  if entry['saved']:shutil.copy2(entry['saved'],path)
  elif path.exists():path.unlink()
 run('nginx','-t');run('systemctl','reload','nginx');run('systemctl','restart','iqs-registration')
 # Imported history and ownership guards intentionally remain safe on routing failure.
 raise
