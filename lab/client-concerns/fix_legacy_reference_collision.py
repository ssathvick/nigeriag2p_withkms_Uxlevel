import json,subprocess,sqlite3,fcntl,sys
from pathlib import Path
root=Path('/opt/openg2p-lab/odk-sync');work=Path(__file__).parent/'legacy-verification'
def run(args):return subprocess.check_output(args,text=True)
deployment=json.loads(run(['kubectl','-n','nigeria','get','deployment','register-staff-portal-api','-o','json']))
backup=root/'legacy-review/before-release/register-staff-portal-api.json'
if not backup.exists():backup.write_text(json.dumps(deployment))
subprocess.run(['kubectl','-n','nigeria','set','env','deployment/register-staff-portal-api','REGISTRY_STAFF_PORTAL_API_APPLICATION_REFERENCE_FORMAT={DATE:%Y%b%d|upper}-{RAND_ALNUM:12}'],check=True)
print('Updated supported application-reference format to a 12-character random suffix; existing references unchanged.')

