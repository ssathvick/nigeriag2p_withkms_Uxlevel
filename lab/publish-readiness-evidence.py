"""Copy only explicitly sanitized engineering summaries to staff readiness view."""
import json,shutil,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
source=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence');target=r.ROOT/'phase1-evidence';target.mkdir(mode=0o700,exist_ok=True)
latest=sorted(source.glob('*-results.json'))[-1];shutil.copy2(latest,target/'automated-tests.json')
for name in ['native-registration-uat','native-reconciliation-uat','native-household-payment','native-mapper-guard-tests','capacity-agents','capacity-native-registry','public-security-performance','browser-readiness','native-programme-concurrency','native-bank-replay','native-statement-recovery','native-statement-backlog']:
 p=source/(name+'.json')
 if p.exists():
  content=json.loads(p.read_text())
  if name=='capacity-native-registry' and content.get('status')!='passed_requested_workload':continue
  if 'samples' in content:content={k:v for k,v in content.items() if k!='samples'}
  saved=target/p.name;saved.write_text(json.dumps(content,indent=2));saved.chmod(0o600)
print('Sanitized evidence copied to existing staff-only readiness view.')
