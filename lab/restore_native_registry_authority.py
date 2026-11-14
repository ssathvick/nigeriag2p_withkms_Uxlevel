"""Return Registry/AWE ownership to native services, retaining migration archives."""
import datetime,json,shutil,subprocess,py_compile
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import RealDictCursor,Json
from test_mbr_db_connection import connect
root=Path('/opt/openg2p-lab/registration')
backup=root/'native-authority-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
def run(*args):return subprocess.run(args,capture_output=True,text=True,check=True)
snapshot=run('/opt/openg2p-lab/registration-venv/bin/python',str(Path(__file__).with_name('snapshot_mbr_migration.py')))
(backup/'snapshot.json').write_text(snapshot.stdout)
run('systemctl','disable','--now','iqs-mbr-native-import.timer')
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT * FROM g2p_mbr_submissions WHERE native_origin IS NULL FOR UPDATE");drafts=q.fetchall()
  if any(d['state']!='DRAFT' or d['payload'].get('members') for d in drafts):raise RuntimeError('Supplemental record requires full section reconciliation')
  q.execute('CREATE TABLE IF NOT EXISTS g2p_native_workflow_legacy_drafts(submission_id uuid PRIMARY KEY,original_record jsonb NOT NULL,migrated_at timestamptz NOT NULL DEFAULT now())')
  q.execute("SELECT * FROM g2p_intake_form_submissions WHERE register_id='a0000000-0000-4000-8000-000000000002' LIMIT 1");template=q.fetchone()
  for d in drafts:
   q.execute('SELECT 1 FROM g2p_native_workflow_legacy_drafts WHERE submission_id=%s',(d['id'],))
   if q.fetchone():continue
   q.execute('SELECT 1 FROM g2p_intake_form_submissions WHERE submission_id=%s',(d['id'],))
   if q.fetchone():raise RuntimeError('Draft ID collision')
   values={'submission_id':d['id'],'application_reference':d['reference'],'form_id':template['form_id'],'register_id':template['register_id'],'draft_status':'DRAFT','approval_status':'PENDING','first_created_at':d['created_at'],'last_updated_at':d['updated_at'],'created_by':d['created_name'],'submission_source':'STAFF_PORTAL','register_ingest_process_status':'NOT_APPLICABLE','register_ingest_process_attempts':0,'number_of_verifications_required':template['number_of_verifications_required'],'number_of_verifications_done':0,'deduplication_status_vs_intake_forms':'NOT_APPLICABLE','deduplication_intake_forms_attempts':0,'deduplication_status_vs_register':'NOT_APPLICABLE','deduplication_register_forms_attempts':0}
   def insert(table,values):
    q.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,values)),sql.SQL(',').join(sql.Placeholder() for _ in values)),list(values.values()))
   insert('g2p_intake_form_submissions',values)
   p=d['payload'];household={'submission_id':d['id'],'application_reference':d['reference'],'internal_record_id':d['id'],'created_by':d['created_name'],'created_at':d['created_at'],'last_approved_at':d['created_at'],'last_approved_by':d['created_name'],'record_status':'ACTIVE','latitude':p.get('latitude'),'longitude':p.get('longitude'),'address_line_1':p.get('address')}
   insert('g2p_intake_form_households',household)
   q.execute('INSERT INTO g2p_native_workflow_legacy_drafts(submission_id,original_record) VALUES(%s,%s)',(d['id'],Json(json.loads(json.dumps(dict(d),default=str)))))
 c.commit()
for database,trigger_names in [('register',['g2p_mbr_write_owner']),('awe',['g2p_mbr_decision_owner','g2p_mbr_task_owner','g2p_mbr_request_owner'])]:
 with connect(database) as c:
  with c.cursor() as q:
   q.execute('SELECT c.relname,t.tgname,pg_get_triggerdef(t.oid) FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid WHERE t.tgname=ANY(%s)',(trigger_names,));triggers=q.fetchall()
   (backup/(database+'-guards.json')).write_text(json.dumps(triggers))
   for table,name,_ in triggers:q.execute(sql.SQL('DROP TRIGGER {} ON {}').format(sql.Identifier(name),sql.Identifier(table)))
  c.commit()
for index,name in enumerate(['/etc/nginx/sites-enabled/iqs-wverve','/etc/nginx/sites-enabled/openg2p-lab']):
 path=Path(name);shutil.copy2(path,backup/('nginx-'+str(index)))
 text=path.read_text();text='\n'.join(line for line in text.split('\n') if '# MBR workflow owner' not in line)
 path.write_text(text)
run('nginx','-t');run('systemctl','reload','nginx')
# Retire the supplemental UI and block its write API; native history remains intact.
path=root/'registration_app.py';shutil.copy2(path,backup/'registration_app.py')
text=path.read_text()
hook='''
# Native Registry is the sole owner of intake, approvals and master updates.
@app.before_request
def native_registry_workflow_owner():
 if request.path.startswith(PREFIX+'/mbr'):
  if request.method not in ('GET','HEAD','OPTIONS'):
   return {'error':'Use the Master Registry for intake, changes and approvals.','registry_url':'https://g2p-register.wverve.in/en'},410
  return redirect('https://g2p-register.wverve.in/en',code=302)
'''
if 'def native_registry_workflow_owner()' not in text:
 text=text.replace('import mbr_workflow\n',hook+'\nimport mbr_workflow\n')
path.write_text(text);py_compile.compile(str(path),doraise=True)
run('systemctl','restart','iqs-registration')
print(json.dumps({'native_registry_authoritative':True,'supplemental_write_api_retired':True,'history_preserved':True,'backup':str(backup)}))
