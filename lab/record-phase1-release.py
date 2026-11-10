import datetime as dt,hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
source=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
files=['registration_app.py','phase1_sandbox.py','phase1_cms.py','phase1_observability.py','phase1_conditionality.py','phase1-worker.py'];hashes={}
for name in files:
 local=hashlib.sha256((source/name).read_bytes()).hexdigest();runtime=hashlib.sha256((r.ROOT/name).read_bytes()).hexdigest();assert local==runtime
 hashes[name]=runtime
workloads=[]
for name in ['bridge-api','bridge-celery-worker','pbms-celery-worker','openg2p-g2p-bridge-example-bank-api','openg2p-g2p-bridge-example-bank-celery']:
 d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']))
 desired=d['spec'].get('replicas',1);ready=d['status'].get('readyReplicas',0);assert ready==desired
 workloads.append({'name':name,'desired_replicas':desired,'ready_replicas':ready,'images':[c['image'] for c in d['spec']['template']['spec']['containers']],'mounted_fixes':[v['configMap']['name'] for v in d['spec']['template']['spec'].get('volumes',[]) if 'configMap' in v and v['configMap']['name'].startswith('phase1-')]})
for unit in ['iqs-registration.service','iqs-phase1.timer']:assert subprocess.check_output(['systemctl','is-active',unit],text=True).strip()=='active'
report={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Deployed source hashes and selected native workload readiness only','source_hashes':hashes,'workloads':workloads,'registration_service':'active','phase1_timer':'active','status':'passed','formal_client_uat':'Not run'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/release-manifest.json').write_text(json.dumps(report,indent=2));print('Deployed source matches and selected native workloads ready; sanitized release manifest saved.')
