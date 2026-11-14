import sys,json,yaml
from pathlib import Path
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
private=Path('/opt/openg2p-lab/registration/android-device-test');account=json.loads((private/'account.json').read_text());assert account['displayName']=='Android acceptance test · 2026-11-13'
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login('https://g2p-odk.wverve.in','admin',password,True)
r=s.delete('https://g2p-odk.wverve.in/v1/projects/1/app-users/'+str(account['id']),timeout=30)
if r.status_code not in [200,404]:r.raise_for_status()
for name in ['account.json','settings.png']:(private/name).unlink(missing_ok=True)
print('Revoked the isolated Android acceptance account and removed its private QR files')
