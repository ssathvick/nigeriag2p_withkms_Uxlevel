from pathlib import Path
import hashlib,json,shutil,sys,datetime,yaml,xml.etree.ElementTree as E
sys.path.insert(0,str(Path(__file__).parent/'client-concerns'))
from test_location_import_e2e import login
ROOT=Path(__file__).parent;dest=Path('/opt/openg2p-lab/odk-sync');backup=dest/('survey-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
xml=(ROOT/'household-parity/nsipa_registry_household.xml').read_bytes();url='https://g2p-odk.wverve.in/v1/projects/1/forms/nsipa_registry_household';password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login('https://g2p-odk.wverve.in','admin',password,True)
r=s.get(url+'.xml',timeout=30);r.raise_for_status();(backup/'previous-form.xml').write_bytes(r.content)
if r.content!=xml:
 r=s.post(url+'/draft',data=xml,headers={'Content-Type':'application/xml'},timeout=45);r.raise_for_status();r=s.post(url+'/draft/publish',timeout=45);r.raise_for_status()
r=s.get(url+'.xml',timeout=30);r.raise_for_status();assert r.content==xml
cfgpath=dest/'config.json';shutil.copy2(cfgpath,backup/'config.json');cfg=json.loads(cfgpath.read_text());cfg.setdefault('definition_sha256',{})['nsipa_registry_household']=hashlib.sha256(xml).hexdigest();cfgpath.write_text(json.dumps(cfg));cfgpath.chmod(0o600)
for src,name in [(ROOT/'client-concerns/odk_native_registry_mapping.py','odk_native_registry_mapping.py'),(ROOT/'household-parity/odk_survey_choices.json','odk_survey_choices.json'),(ROOT/'field-app/android/assets/locations.json','nigeria_locations.json'),(ROOT/'household-parity/mobile-geo-crosswalk.json','mobile-geo-crosswalk.json')]:
 if (dest/name).exists():shutil.copy2(dest/name,backup/name)
 shutil.copy2(src,dest/name)
definition=E.fromstring(xml);instance=definition.find('.//{http://www.w3.org/2002/xforms}instance/data')
field_count=len(json.loads((ROOT/'household-parity/odk_survey_choices.json').read_text())['paths'])
print(json.dumps({'status':'published','version':instance.get('version'),'fields':field_count,'stateLgaWardChoices':True,'priorFormVersionRetained':True}))
