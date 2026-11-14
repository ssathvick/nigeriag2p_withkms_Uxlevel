import subprocess,json,ast
from pathlib import Path
root=Path(__file__).parent;rel='reference/services/g2p_register_domain_service_individual.py';p=root/'meeting-native/patched/register-staff-portal-api'/rel;p.parent.mkdir(parents=True,exist_ok=True);target='/usr/local/lib/python3.12/site-packages/openg2p_registry_reference_extension/register_domain/services/g2p_register_domain_service_individual.py'
run=lambda *a,input=None:subprocess.run(a,input=input,text=True,capture_output=True,check=True).stdout
if not p.exists():p.write_text(run('kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','cat',target))
s=p.read_text().replace('            validation_error("middle_name is required")','            return  # Other/middle names are optional in the household survey.');ast.parse(s);p.write_text(s)
cm=json.loads(run('kubectl','-n','nigeria','get','cm','native-household-parity','-o','json'));cm['data']['f4']=s;run('kubectl','replace','-f','-',input=json.dumps(cm))
for dep in ['register-staff-portal-api','register-celery-worker','register-celery-beat-producer','register-partner-api','registry-bg-tasks-worker','registry-bg-tasks-producer','register-id-generator']:
 d=json.loads(run('kubectl','-n','nigeria','get','deploy',dep,'-o','json'));container=d['spec']['template']['spec']['containers'][0];mount={'name':'native-household-parity','mountPath':target,'subPath':'f4','readOnly':True};container['volumeMounts']=[m for m in container['volumeMounts'] if m['mountPath']!=target]+[mount];run('kubectl','replace','-f','-',input=json.dumps(d))
changes=root/'meeting-native/changes.json';m=json.loads(changes.read_text());m['register-staff-portal-api']['patched/register-staff-portal-api/'+rel]=target;changes.write_text(json.dumps(m,indent=2))
print('Aligned optional other/middle names with the video and native form schema')
