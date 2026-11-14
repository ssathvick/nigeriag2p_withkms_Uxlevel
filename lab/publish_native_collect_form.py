import hashlib,json,shutil,sys,yaml
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'client-concerns'))
from test_location_import_e2e import login
ROOT=Path(__file__).parent;dest=Path('/opt/openg2p-lab/odk-sync');cfgpath=dest/'config.json';cfg=json.loads(cfgpath.read_text());fid='nsipa_registry_household';xml=(ROOT/'meeting-native'/ (fid+'.xml')).read_bytes()
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login('https://g2p-odk.wverve.in','admin',password,True)
url='https://g2p-odk.wverve.in/v1/projects/1/forms';r=s.get(url,timeout=30);r.raise_for_status()
if not any(f['xmlFormId']==fid for f in r.json()):
 r=s.post(url+'?publish=true',data=xml,headers={'Content-Type':'application/xml'},timeout=45);r.raise_for_status()
r=s.get(url+'/'+fid+'.xml',timeout=30);r.raise_for_status()
if r.content!=xml:raise RuntimeError('Published native field form differs from reviewed definition')
shutil.copy2(cfgpath,dest/'config-before-native-form.json')
if fid not in cfg['forms']:cfg['forms'].append(fid)
cfg.setdefault('definition_sha256',{})[fid]=hashlib.sha256(xml).hexdigest();cfgpath.write_text(json.dumps(cfg));cfgpath.chmod(0o600)
for name in ['odk_native_registry_mapping.py','odk_household_mapping.py','odk_sync_worker.py']:shutil.copy2(ROOT/'client-concerns'/name,dest/name)
shutil.copy2(ROOT/'native_offline_setup.py',Path('/opt/openg2p-lab/registration/native_offline_setup.py'))
print('Published full native household offline form and enabled native section synchronization.')
