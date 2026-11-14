import sys,json,zlib,base64,datetime
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import qrcode,yaml
sys.path.insert(0,str(Path(__file__).parent/'client-concerns'))
from test_location_import_e2e import login
ROOT=Path(__file__).parent;out=ROOT.parent/'output/android-flow-verification';private=Path('/opt/openg2p-lab/registration/android-device-test');private.mkdir(mode=0o700,exist_ok=True);origin='https://g2p-odk.wverve.in';password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login(origin,'admin',password,True);label='Android acceptance test · 2026-11-13';r=s.get(origin+'/v1/projects/1/app-users',timeout=30);r.raise_for_status();account=next((a for a in r.json() if a['displayName']==label and a.get('token')),None)
if account is None:r=s.post(origin+'/v1/projects/1/app-users',json={'displayName':label},timeout=30);r.raise_for_status();account=r.json()
r=s.get(origin+'/v1/roles',timeout=30);r.raise_for_status();role=next(x for x in r.json() if x.get('system')=='app-user');r=s.post(origin+f"/v1/projects/1/forms/nsipa_registry_household/assignments/{role['id']}/{account['id']}",timeout=30);assert r.status_code in [200,201,409]
settings={'project':{'name':'NSIPA Android acceptance test','color':'#155e50'},'general':{'server_url':origin+'/v1/key/'+account['token']+'/projects/1','autosend':'wifi_and_cellular','delete_send':False,'default_completed':False,'metadata_username':'Android dummy-data test','form_update_mode':'previously_downloaded','automatic_update':True,'navigation':'buttons'},'admin':{}}
(private/'account.json').write_text(json.dumps(account));(private/'account.json').chmod(0o600);img=qrcode.make(base64.b64encode(zlib.compress(json.dumps(settings).encode())).decode());img.save(private/'settings.png');(private/'settings.png').chmod(0o600)
# Temporary phone import file, excluded from the verification artifacts.
copy=ROOT/'field-app/android/tools/private-android-settings.png';copy.write_bytes((private/'settings.png').read_bytes());print('Created isolated, scoped Android test project QR; token excluded from output')
