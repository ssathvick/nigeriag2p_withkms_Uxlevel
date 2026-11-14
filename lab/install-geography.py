"""Add geographic catalogue/views and intake capture, preserving existing workflow states."""
from pathlib import Path
import datetime,shutil,sqlite3,subprocess,json,base64,os,sys
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');sys.path.insert(0,str(src));from labdb import query
root=Path('/opt/openg2p-lab/registration');backup=root/'geography-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
shutil.copytree(root/'templates',backup/'templates');shutil.copytree(root/'static',backup/'static')
for name in ['registration_app.py','registration_workspaces.py','nigeria_geography.py','nigeria-geography.json']:
 if (root/name).exists():shutil.copy2(root/name,backup/name)
secret=json.loads(subprocess.check_output(['kubectl','get','secret','commons-postgresql','-n','nigeria','-o','json']));ip=subprocess.check_output(['kubectl','get','svc','commons-postgresql','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip();env=dict(os.environ,PGPASSWORD=base64.b64decode(secret['data']['postgres-password']).decode())
with (backup/'register.dump').open('wb') as dump:
 subprocess.run(['kubectl','exec','-i','-n','nigeria','commons-postgresql-0','--','bash','-c','read -r PGPASSWORD; export PGPASSWORD; exec pg_dump -U postgres -d register -Fc'],input=(env['PGPASSWORD']+'\n').encode(),stdout=dump,stderr=subprocess.PIPE,check=True)
query('register',(src/'geography/migration.sql').read_text(encoding='utf-8'))
subprocess.run(['systemctl','stop','iqs-registration.service'],check=True)
try:
 with sqlite3.connect(root/'intake.sqlite') as source,sqlite3.connect(backup/'intake.sqlite') as target:source.backup(target)
 for name in ['registration_app.py','registration_workspaces.py','nigeria_geography.py','nigeria-geography.json']:shutil.copy2(src/name,root/name)
 for name in ['profile.html','geography.html']:shutil.copy2(src/'registration-ui'/name,root/'templates'/name)

 for asset in ['geography-map.js','geography-map.css','nigeria-states.geojson']:shutil.copy2(src/'registration-ui'/asset,root/'static'/asset)
 shutil.copy2(src/'registration-ui/geo-form.js',root/'static/geo-form.js');shutil.copy2(src/'persona-ui/dist/workspace.js',root/'static/workspace.js')
 # Preserve case states, maker identity and coordinate absence. Derive only known administrative attributes.
 import nigeria_geography as geo
 count=0;unknown=0
 with sqlite3.connect(root/'intake.sqlite') as c:
  for sub,reference,data in c.execute('SELECT sub,household_ref,data FROM profiles').fetchall():
   d=json.loads(data)
   try:g=geo.geography(d)
   except ValueError:unknown+=1;continue
   if d.get('geography')==g:continue
   d['geography']=g;stamp=datetime.datetime.now(datetime.timezone.utc).isoformat();c.execute('UPDATE profiles SET data=?,updated=? WHERE sub=?',(json.dumps(d),stamp,sub));c.execute("INSERT INTO audit(actor,action,reference,at) VALUES('system','geography_metadata_added',?,?)",(reference,stamp));count+=1
 subprocess.run([str(root.parent/'registration-venv/bin/python'),'-m','py_compile',str(root/'registration_app.py'),str(root/'registration_workspaces.py'),str(root/'nigeria_geography.py')],check=True)
 print('Geographic data preparation installed. Intake profiles enriched:',count,'Unmapped profiles:',unknown)
 print('Private source/SQLite/PostgreSQL snapshot:',backup)
finally:subprocess.run(['systemctl','start','iqs-registration.service'],check=True)
print(query('register',"SELECT record_type,sum(record_count),sum(coordinates_present) FROM ng2p_geography_record_counts GROUP BY record_type ORDER BY record_type;"))
