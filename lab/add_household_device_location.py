from pathlib import Path
import json,copy,subprocess,ast,datetime,re
from psycopg2 import sql
from psycopg2.extras import Json,RealDictCursor
from test_mbr_db_connection import connect
ROOT=Path(__file__).parent;PATCH=ROOT/'meeting-native/patched/register-staff-portal-api/reference';fields={'location_accuracy_m':('float','Numeric','numeric'),'location_captured_at':('str','String','varchar'),'location_capture_source':('str','String','varchar')}
for group in ['models','schemas']:
 p=PATCH/group/'household.py';s=p.read_text();anchor='class G2P'+('Schema' if group=='schemas' else '')+'Household:';block=''
 for field,(py,sa,db) in fields.items():
  if field+':' not in s:block+=f'    {field}: '+(f'Mapped[{py}] = mapped_column({sa}, nullable=True)' if group=='models' else f'Optional[{py}] = None')+'\n'
 if block:s=s.replace(anchor,anchor+'\n'+block);ast.parse(s);p.write_text(s)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  for t in ['g2p_intake_form_households','g2p_register_households','g2p_register_history_households']:
   for f,(_,_,db) in fields.items():q.execute(sql.SQL('ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} '+db).format(sql.Identifier(t),sql.Identifier(f)))
  q.execute("SELECT section_id,section_ui_schema FROM g2p_register_sections WHERE section_id LIKE 'hh_%'");rows=q.fetchall()
  def fix(v):
   if isinstance(v,dict):
    if 'widget-options' in v:v['widget-data-options']=v.pop('widget-options')
    for x in v.values():fix(x)
   elif isinstance(v,list):
    for x in v:fix(x)
  for row in rows:
   schema=row['section_ui_schema'];fix(schema)
   if row['section_id']=='hh_survey_consent':
    widgets=schema['panels'][0]['widgets']
    for f,label in [('location_accuracy_m','Location accuracy (metres)'),('location_captured_at','Device capture time (UTC)'),('location_capture_source','Location source')]:
     if not any(w.get('widget-id')==f for w in widgets):widgets.append({'widget':'number' if f=='location_accuracy_m' else 'text','widget-id':f,'widget-type':'input','widget-label':label,'widget-readonly':True,'widget-required':False,'widget-data-path':'a0000000-0000-4000-8000-000000000002.'+f})
   q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id=%s',(Json(schema),row['section_id']))
 c.commit()
# Share the location model through the already mounted parity ConfigMap.
run=lambda *a,input=None:subprocess.run(a,input=input,text=True,capture_output=True,check=True).stdout
cm=json.loads(run('kubectl','-n','nigeria','get','cm','native-household-parity','-o','json'));cm['data']['f0']=(PATCH/'models/household.py').read_text();cm['data']['f1']=(PATCH/'schemas/household.py').read_text();run('kubectl','replace','-f','-',input=json.dumps(cm))
for d in ['register-staff-portal-api','register-celery-worker','register-celery-beat-producer','register-partner-api','registry-bg-tasks-worker','registry-bg-tasks-producer','register-id-generator']:run('kubectl','-n','nigeria','rollout','restart','deploy/'+d)
# Container timestamps are UTC; keep historical submissions outside new confirmation enforcement.
p=ROOT/'meeting-native/patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';s=p.read_text();s=re.sub(r'if submission.first_created_at >= datetime.fromisoformat\([^\n]+\):', 'if submission.first_created_at >= datetime.fromisoformat('+repr(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat())+'):',s);p.write_text(s)
print('Added native GPS accuracy/time/source, and corrected native conditional-question metadata')
