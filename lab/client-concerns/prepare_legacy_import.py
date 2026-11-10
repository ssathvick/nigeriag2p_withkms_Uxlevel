import sys,json,hashlib,fcntl,sqlite3,shutil,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/odk-sync')
from odk_sync_worker import Client,ROOT
sys.path.insert(0,str(Path(__file__).parent))
from odk_legacy_mapping import map_legacy
from odk_household_mapping import parse_xml
src=Path(__file__).parent;work=src/'legacy-verification';work.mkdir(exist_ok=True)
cfg=json.loads((ROOT/'config.json').read_text());inventory=json.loads((ROOT/'legacy-review/inventory.json').read_text())
assert len(inventory)==5
names=['Idris Ahmed','Ngozi Eze','Mariam Lawal','Tunde Bakare','Grace Okon'];manifest={};evidence=[]
client=Client(cfg)
try:
 master={key:client.post('/attributes/get_attribute_values',{'attribute_id':key},client.master) for key in ['ROOF_MATERIAL','WATER_SOURCE_TYPE']}
 for item,name in zip(inventory,names):
  xml=(ROOT/'legacy-review'/(item['instance'].replace(':','_')+'.xml')).read_bytes();definition=(ROOT/'legacy-review'/('definition-'+item['version']+'.xml')).read_bytes();data=parse_xml(xml)
  review={'instance_id':item['instance'],'form_id':data.get('id'),'form_version':item['version'],'source_sha256':hashlib.sha256(xml).hexdigest(),'definition_file':'definition-'+item['version']+'.xml','definition_sha256':hashlib.sha256(definition).hexdigest(),'authorization':'User explicitly requested synthetic household and head names','synthetic_names':{'household_name':'Synthetic '+name+' Household (legacy demo)','household_head_name':'Synthetic '+name}}
  mapped=map_legacy(xml,definition,master,review);manifest[item['instance']]=review
  evidence.append({'instance':item['instance'],'sample_reference':data.findtext('household/sample_reference'),'review':review,'mapping':mapped})
 (work/'approved-mappings.json').write_text(json.dumps(evidence,indent=2));(work/'master.json').write_text(json.dumps(master));print('Prepared five exact-source synthetic mappings; originals preserved.')
finally:client.close()
if '--deploy' not in sys.argv:sys.exit(0)
subprocess.run(['systemctl','stop','nsipa-odk-sync.timer'],check=True)
try:
 with open(ROOT/'worker.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  backup=ROOT/'legacy-review/before-release';backup.mkdir(mode=0o700,exist_ok=True)
  for name in ['config.json','odk_sync_worker.py']:
   if not (backup/name).exists():shutil.copy2(ROOT/name,backup/name)
  c=sqlite3.connect(ROOT/'ledger.sqlite');c.row_factory=sqlite3.Row
  b=sqlite3.connect(backup/'ledger.sqlite');c.backup(b);b.close()
  for instance,review in manifest.items():
   row=c.execute('SELECT * FROM imports WHERE instance_id=?',(instance,)).fetchone();assert row and row['source_hash']==review['source_sha256'];assert not row['submission_id']
   assert row['state']=='QUARANTINED'
  cfg['legacy_reviews']=manifest;(ROOT/'config.json').write_text(json.dumps(cfg));(ROOT/'config.json').chmod(0o600)
  for name in ['odk_sync_worker.py','odk_legacy_mapping.py']:shutil.copy2(src/name,ROOT/name)
  for instance in manifest:c.execute("UPDATE imports SET state='DISCOVERED',error=NULL WHERE instance_id=?",(instance,))
  c.commit();c.close();(ROOT/'legacy-review/approved-mappings.json').write_text(json.dumps(evidence,indent=2))
 print('Released only the five authorized source hashes; timer resumes existing two-reviewer intake flow.')
finally:subprocess.run(['systemctl','start','nsipa-odk-sync.timer'],check=True)
