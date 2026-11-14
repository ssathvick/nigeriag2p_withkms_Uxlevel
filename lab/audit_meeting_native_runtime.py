import json,subprocess
from pathlib import Path
from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
OUT=Path(__file__).parent.parent/'output/ooru-meeting-audit/native';OUT.mkdir(parents=True,exist_ok=True)
def run(*args):return subprocess.check_output(args,text=True)
report={}
for deployment in ['register-staff-portal-ui','register-staff-portal-api','commons-services-awe']:
 d=json.loads(run('kubectl','-n','nigeria','get','deploy',deployment,'-o','json'))
 report[deployment]={'containers':[{k:v for k,v in x.items() if k in ['name','image','volumeMounts','env']} for x in d['spec']['template']['spec']['containers']],'volumes':d['spec']['template']['spec'].get('volumes')}
 # Never write environment values to audit output.
 for c in report[deployment]['containers']:c['env']=[x['name'] for x in c.get('env',[])]
for deployment,base,files in [('register-staff-portal-api','/usr/local/lib/python3.12/site-packages/openg2p_registry_core/',['services/intake_form_data_service.py','services/g2p_awe_webhook_service.py','services/g2p_awe_integration_service.py','services/g2p_awe_proxy_service.py','schemas/awe_task.py','services/g2p_register_change_request_service.py']),('commons-services-awe','/usr/local/lib/python3.13/site-packages/awe/',['services/engine.py','routers/tasks.py','schemas/tasks.py'])]:
 for f in files:
  try:(OUT/(deployment+'-'+Path(f).name)).write_text(run('kubectl','-n','nigeria','exec','deploy/'+deployment,'--','cat',base+f))
  except subprocess.CalledProcessError:pass
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  for table in ['g2p_intake_form_definitions','g2p_intake_form_ui_tabs','g2p_intake_form_ui_tab_sections','g2p_register_sections']:
   q.execute('SELECT * FROM '+table);(OUT/(table+'.json')).write_text(json.dumps(q.fetchall(),default=str,indent=2))
(OUT/'runtime.json').write_text(json.dumps(report,indent=2));print('Native runtime and form metadata captured without credentials.')
