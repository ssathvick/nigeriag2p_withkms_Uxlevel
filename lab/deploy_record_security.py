"""Back up native data/deployment, install additive RLS, then mount request enforcement."""
from pathlib import Path
import datetime,json,subprocess
from record_security_secret import signing_environment
from test_mbr_db_connection import connect
root=Path(__file__).parent/'record-security'
def run(*args,input=None):return subprocess.check_output(args,input=input,text=True)
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=Path('/opt/openg2p-lab/registration/record-security-backups')/stamp;backup.mkdir(parents=True,mode=0o700)
d=json.loads(run('kubectl','-n','nigeria','get','deploy','register-staff-portal-api','-o','json'));(backup/'deployment.json').write_text(json.dumps(d))
for db in ['register','awe','iam']:
 with (backup/(db+'.dump')).open('wb') as output:
  subprocess.run(['kubectl','-n','nigeria','exec','commons-postgresql-0','--','bash','-c','export PGPASSWORD="$POSTGRES_POSTGRES_PASSWORD"; exec pg_dump -U postgres -Fc "$1"','security-backup',db],stdout=output,check=True)
 (backup/(db+'.dump')).chmod(0o600)
with connect() as c:
 with c.cursor() as q:
  q.execute((root/'schema.sql').read_text());q.execute((root/'policies.sql').read_text())
 c.commit()
files={'scope':(root/'record_scope.py','/usr/local/lib/python3.12/site-packages/openg2p_registry_core/record_scope.py'),
 'main':(root/'registry-main.py','/usr/local/lib/python3.12/site-packages/openg2p_registry_staff_api/main.py'),
 'proxy':(root/'g2p_awe_proxy_controller_service.py','/usr/local/lib/python3.12/site-packages/openg2p_registry_core/controller_services/g2p_awe_proxy_controller_service.py'),
 'intake':(root/'intake_form_data_controller_service.py','/usr/local/lib/python3.12/site-packages/openg2p_registry_core/controller_services/intake_form_data_controller_service.py'),
 'helper':(root/'awe_helper.py','/usr/local/lib/python3.12/site-packages/openg2p_registry_core/helpers/awe_helper.py')}
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nsipa-record-security','namespace':'nigeria'},'data':{key:path.read_text() for key,(path,target) in files.items()}}
run('kubectl','apply','-f','-',input=json.dumps(cm))
spec=d['spec']['template']['spec'];container=spec['containers'][0];targets={target for path,target in files.values()}
signing_environment(container)
spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!='nsipa-record-security']+[{'name':'nsipa-record-security','configMap':{'name':'nsipa-record-security'}}]
container['volumeMounts']=[m for m in container.get('volumeMounts',[]) if m['name']!='nsipa-record-security' and m['mountPath'] not in targets]+[{'name':'nsipa-record-security','mountPath':target,'subPath':key,'readOnly':True} for key,(path,target) in files.items()]
d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['nsipa-record-security']=stamp
run('kubectl','replace','-f','-',input=json.dumps(d));run('kubectl','-n','nigeria','rollout','status','deployment/register-staff-portal-api','--timeout=240s')
(root/'deployment.json').write_text(json.dumps({'backup':str(backup),'release':stamp}))
print('Record security deployed. Private recovery point:',backup)
