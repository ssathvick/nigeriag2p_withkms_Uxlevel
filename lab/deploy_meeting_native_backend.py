"""Apply additive native schema/metadata and backed-up Registry/AWE module mounts."""
import ast,datetime,hashlib,json,subprocess
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import Json,RealDictCursor
from test_mbr_db_connection import connect
ROOT=Path(__file__).parent;changes=json.loads((ROOT/'meeting-native/changes.json').read_text())
backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
def run(*args,input=None):return subprocess.run(args,input=input,capture_output=True,text=True,check=True).stdout
snapshot=run('/opt/openg2p-lab/registration-venv/bin/python',str(ROOT/'snapshot_mbr_migration.py'));(backup/'snapshot.json').write_text(snapshot)
fields=['sponsor_name','consent_status','respondent_name','enumerator_name','survey_community','health_insurance_status','income_source']
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute('CREATE TABLE IF NOT EXISTS g2p_registry_return_history(event_id text PRIMARY KEY,artifact_id text NOT NULL,artifact_type text NOT NULL,request_id text NOT NULL,actor text,reason text,payload jsonb,created_at timestamptz NOT NULL DEFAULT now())')
  q.execute('CREATE TABLE IF NOT EXISTS g2p_registry_review_comments(event_id text PRIMARY KEY,comment text NOT NULL)')
  for table in ['g2p_intake_form_households','g2p_register_households','g2p_register_history_households']:
   for field in fields:q.execute(sql.SQL('ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} varchar').format(sql.Identifier(table),sql.Identifier(field)))
   q.execute(sql.SQL('ALTER TABLE {} ADD COLUMN IF NOT EXISTS monthly_household_income numeric').format(sql.Identifier(table)))
  q.execute("SELECT * FROM g2p_register_sections WHERE section_id IN ('hh_composition_headship','hh_members','hh_dwelling_services') FOR UPDATE");sections=q.fetchall();(backup/'sections.json').write_text(json.dumps(sections,default=str))
  for section in sections:
   schema=section['section_ui_schema']
   if section['section_id']=='hh_composition_headship':
    panels=schema['panels'][0]['panels']
    for index,field in enumerate(fields[:5]):
     if field=='enumerator_name':continue
     if any(w.get('widget-id')==field for p in panels for w in p.get('widgets',[])):continue
     w={'widget':'select' if field=='consent_status' else 'text','widget-id':field,'widget-type':'input','widget-label':field,'widget-readonly':False,'widget-required':field!='survey_community','widget-data-path':section['section_register_id']+'.'+field}
     if field=='consent_status':w['widget-data-source']={'type':'static','options':[{'label':'Yes — informed consent given','value':'YES'},{'label':'No — stop the interview','value':'NO'}]}
     panels[1 if index<3 else 2]['widgets'].append(w)
   elif section['section_id']=='hh_members':
    columns=schema['panels'][0]['widgets'][0]['widget-data-columns']
    for w in columns:
     if w.get('column-key')=='birth_date':w['widget-required']=False
    if not any(w.get('column-key')=='estimated_age' for w in columns):columns.append({'widget':'number','column-key':'estimated_age','widget-label':'Age (if date of birth unknown)','widget-required':False,'widget-data-path':'estimated_age'})
    relationship=next((w for w in columns if w.get('column-key')=='relationship_to_head'),None)
    if not relationship:
     relationship={'widget':'select','column-key':'relationship_to_head','widget-label':'relationship_to_head','widget-required':False,'widget-data-path':'relationship_to_head'};columns.append(relationship)
    relationship['widget-data-source']={'type':'static','options':[{'label':'Household head' if x=='SELF' else x.title().replace('_',' '),'value':x} for x in ['SELF','SPOUSE','CHILD','PARENT','SIBLING','OTHER_RELATIVE','NON_RELATIVE']]}
   else:
    panel=schema['panels'][0]
    while panel.get('panels'):panel=panel['panels'][-1]
    widgets=panel.setdefault('widgets',[])
    for field,label,widget in [('monthly_household_income','monthly_household_income','number'),('income_source','income_source','text'),('health_insurance_status','health_insurance_status','select')]:
     if any(w.get('widget-id')==field for w in widgets):continue
     w={'widget':widget,'widget-id':field,'widget-type':'input','widget-label':label,'widget-required':False,'widget-data-path':section['section_register_id']+'.'+field}
     if widget=='select':w['widget-data-source']={'type':'static','options':[{'label':x.title(),'value':x} for x in ['YES','NO','UNKNOWN']]}
     widgets.append(w)
   q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id=%s',(Json(schema),section['section_id']))
 c.commit()
def mount(deployment,files):
 d=json.loads(run('kubectl','-n','nigeria','get','deploy',deployment,'-o','json'));(backup/(deployment+'.json')).write_text(json.dumps(d))
 name='native-meeting-'+deployment;data={};mounts=[]
 for i,(source,target) in enumerate(files.items()):
  value=(ROOT/'meeting-native'/source).read_text();ast.parse(value);key='f'+str(i);data[key]=value;mounts.append({'name':name,'mountPath':target,'subPath':key,'readOnly':True})
 cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':name,'namespace':'nigeria'},'data':data}
 run('kubectl','apply','--server-side','--field-manager=native-meeting','-f','-',input=json.dumps(cm))
 spec=d['spec']['template']['spec'];container=spec['containers'][0]
 spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!=name]+[{'name':name,'configMap':{'name':name}}]
 targets=set(files.values());container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['name']!=name and v['mountPath'] not in targets]+mounts
 d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['native-meeting-sha']=hashlib.sha256(json.dumps(data).encode()).hexdigest()
 run('kubectl','replace','-f','-',input=json.dumps(d))
for deployment,files in changes.items():mount(deployment,files)
reference={s:t for s,t in changes['register-staff-portal-api'].items() if 'openg2p_registry_reference_extension' in t}
for deployment in ['register-celery-worker','register-celery-beat-producer','register-partner-api','registry-bg-tasks-worker','registry-bg-tasks-producer','register-id-generator']:mount(deployment,reference)
(ROOT/'meeting-native/latest-backup.txt').write_text(str(backup));print(json.dumps({'backup':str(backup),'native_services_updated':len(changes)+6,'schema':'additive','history':'preserved'}))
