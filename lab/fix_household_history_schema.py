import ast,json,subprocess,datetime
from pathlib import Path
ROOT=Path(__file__).parent;source=ROOT/'meeting-native/patched/register-staff-portal-api/reference/schemas/household.py';value=source.read_text();ast.parse(value)
def run(*args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
cm=json.loads(run('kubectl','-n','nigeria','get','cm','native-household-parity','-o','json'));assert 'class G2PRegisterHistorySchemaHousehold' in cm['data']['f1']
backup=Path('/opt/openg2p-lab/registration/history-schema-backups');backup.mkdir(mode=0o700,exist_ok=True);(backup/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')).write_text(json.dumps(cm));cm['data']['f1']=value;run('kubectl','replace','-f','-',input=json.dumps(cm))
deps=['register-staff-portal-api','register-celery-worker','register-celery-beat-producer','register-partner-api','registry-bg-tasks-worker','registry-bg-tasks-producer','register-id-generator'];run('kubectl','-n','nigeria','rollout','restart',*['deployment/'+d for d in deps]);print('Updated household history domain schema; no existing history rows changed')
for d in deps:run('kubectl','-n','nigeria','rollout','status','deployment/'+d,'--timeout=120s')
print('All seven registry deployments ready')
