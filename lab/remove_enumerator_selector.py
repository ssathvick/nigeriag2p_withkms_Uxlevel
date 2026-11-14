"""Remove the survey selector without deleting captured values or history."""
import ast,datetime,json,subprocess
from pathlib import Path
from psycopg2.extras import Json,RealDictCursor
from test_mbr_db_connection import connect
ROOT=Path(__file__).parent
def run(*args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/('remove-enumerator-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
def remove(node):
 if isinstance(node,dict):
  for key,value in list(node.items()):
   if key=='widgets' and isinstance(value,list):node[key]=[w for w in value if w.get('widget-id')!='enumerator_name']
   remove(node[key])
 elif isinstance(node,list):
  for child in node:remove(child)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT section_id,section_ui_schema FROM g2p_register_sections WHERE section_id IN ('hh_composition_headship','hh_survey_consent') FOR UPDATE");rows=q.fetchall();(backup/'sections.json').write_text(json.dumps(rows,default=str))
  for row in rows:
   schema=row['section_ui_schema'];remove(schema);q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id=%s',(Json(schema),row['section_id']))
 c.commit()
source=ROOT/'meeting-native/patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';ast.parse(source.read_text())
d=json.loads(run('kubectl','-n','nigeria','get','deploy','register-staff-portal-api','-o','json'));spec=d['spec']['template']['spec'];target='/usr/local/lib/python3.12/site-packages/openg2p_registry_core/services/intake_form_data_service.py'
mount=next(m for m in spec['containers'][0]['volumeMounts'] if m['mountPath']==target);volume=next(v for v in spec['volumes'] if v['name']==mount['name']);cmname=volume['configMap']['name'];cm=json.loads(run('kubectl','-n','nigeria','get','configmap',cmname,'-o','json'));(backup/'backend-configmap.json').write_text(json.dumps(cm));cm['data'][mount['subPath']]=source.read_text();run('kubectl','replace','-f','-',input=json.dumps(cm));run('kubectl','-n','nigeria','rollout','restart','deployment/register-staff-portal-api')
print(json.dumps({'selector_removed':True,'captured_values_modified':0,'backup':str(backup)}))
