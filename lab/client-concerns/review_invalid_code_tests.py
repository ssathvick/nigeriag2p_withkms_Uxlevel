import sys,json,hashlib,uuid,sqlite3,fcntl,shutil
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,'/opt/openg2p-lab/odk-sync');from odk_sync_worker import Client,ROOT
from odk_household_mapping import map_submission,parse_xml,choices
src=Path(__file__).parent;work=src/'invalid-code-review';work.mkdir(exist_ok=True)
prior=src/'auto-sync-verification';original_state=json.loads((prior/'state.json').read_text())['0-numeric'];original=(prior/'0-numeric-source.xml').read_bytes()
targets=[x for x in json.loads((prior/'replay-and-invalid.json').read_text()) if 'invalidNumericInstance' in x];assert len(targets)==2
cfg=json.loads((ROOT/'config.json').read_text());evidence=[]
for host in ['odk.nigeriag2p.com','g2p-odk.wverve.in']:
 client=Client({**cfg,'odk_origin':'https://'+host})
 try:
  definition=client.get('/v1/projects/1/forms/nsipa_household_mapping_check.xml').content
  master={k:client.post('/attributes/get_attribute_values',{'attribute_id':k},client.master) for k in ['ROOF_MATERIAL','WATER_SOURCE_TYPE']}
  opts=choices(parse_xml(definition),'/data/household/roof_material');assert '999' not in opts;assert opts['2']=='Corrugated iron'
  for target in targets:
   instance=target['invalidNumericInstance'];xml=client.get('/v1/projects/1/forms/nsipa_household_mapping_check/submissions/'+quote(instance,safe='')+'.xml').content
   expected=original.replace(original_state['instance'].encode(),instance.encode()).replace(b'<roof_material>2</roof_material>',b'<roof_material>999</roof_material>')
   assert xml==expected,'Source must exactly match the documented negative-test mutation'
   try:map_submission(xml,definition,master)
   except ValueError as e:assert str(e)=='Unmapped source choice: 999'
   else:raise AssertionError('Invalid code must remain rejected')
   internal=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-odk:nsipa_household_mapping_check:'+instance))
   evidence.append({'host':host,'instance':instance,'internal_id':internal,'source_sha256':hashlib.sha256(xml).hexdigest(),'matches_documented_negative_test':True,'invalid_value':'999','validation_still_rejects':True,'valid_source_instance':original_state['instance'],'valid_source_internal_id':original_state['mapping']['payload']['internal_record_id'],'disposition':'EXCLUDED_TEST'})
 finally:client.close()
(work/'source-review.json').write_text(json.dumps(evidence,indent=2));print('Verified both negative fixtures through both ODK domains; code 999 remains rejected.')
if '--apply' not in sys.argv:sys.exit(0)
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as app
with open(ROOT/'worker.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 c=sqlite3.connect(ROOT/'ledger.sqlite');c.row_factory=sqlite3.Row;backup=ROOT/'invalid-code-review';backup.mkdir(mode=0o700,exist_ok=True)
 b=sqlite3.connect(backup/'ledger-before.sqlite');c.backup(b);b.close();shutil.copy2(ROOT/'odk_sync_worker.py',backup/'worker-before.py')
 audited=[]
 with app.pg('register') as db:
  with db.cursor() as q:
   q.execute('SELECT count(*) FROM g2p_register_households WHERE internal_record_id=%s',(original_state['mapping']['payload']['internal_record_id'],));assert q.fetchone()[0]==1
   for item in evidence[:2]:
    row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(item['instance'],)).fetchone());assert row['source_hash']==item['source_sha256'];assert row['submission_id'] is None;assert row['state']=='QUARANTINED'
    for table in ['g2p_intake_form_households','g2p_register_households']:
     q.execute('SELECT count(*) FROM '+table+' WHERE internal_record_id=%s',(item['internal_id'],));assert q.fetchone()[0]==0
    audited.append({'before':row,'review':item,'reason':'Intentional negative-code clone of an already imported synthetic test source. No new household; exclude from import while preserving source and validation evidence.'})
 (backup/'resolution-audit.json').write_text(json.dumps(audited,indent=2));(work/'resolution-audit.json').write_text(json.dumps(audited,indent=2))
 shutil.copy2(src/'odk_sync_worker.py',ROOT/'odk_sync_worker.py')
 for item in evidence[:2]:c.execute("UPDATE imports SET state='EXCLUDED_TEST',error='Reviewed intentional invalid-code test; original source preserved; not an importable household',updated_at=datetime('now') WHERE instance_id=?",(item['instance'],))
 c.commit();c.close()
print('Resolved the two fixtures as EXCLUDED_TEST, without changing ODK XML or creating duplicate households.')
