"""User-authorized, exact-source backfill for HH-7574890659 only.

Keep original intake, approvals and V0 history unchanged. Record a separate
administrative repair receipt; do not impersonate an approval reviewer.
"""
import sys,json,hashlib,os,datetime,fcntl
from pathlib import Path
from odk_geography import load_geography
from odk_household_mapping import map_submission
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
RID='18023d14-0bc7-51a7-b51b-9f9b77ef8a05'
ROOT=Path('/opt/openg2p-lab/odk-sync')
def main():
 os.umask(0o077)
 evidence=ROOT/'receipts'/RID
 original=json.loads((evidence/'mapping.json').read_text())
 source=(evidence/'source.xml').read_bytes()
 assert hashlib.sha256(source).hexdigest()==original['source_sha256']
 mapped=map_submission(source,(evidence/'definition.xml').read_bytes(),{'GEO_VALUES':load_geography(),'ROOF_MATERIAL':[],'WATER_SOURCE_TYPE':[]})
 assert mapped['payload']['internal_record_id']==RID
 assert mapped['payload']['record_name']=='household synthetic fault test'
 fields={k:mapped['payload'][k] for k in ('geo_lowest_level_value_id','geo_code_hierarchy_json')}
 assert fields['geo_lowest_level_value_id']=='OCHA-NG032005'
 timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 path=evidence/'location-repair-2026-11-12.json'
 with open(ROOT/'worker.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with r.pg('register') as c:
   with c.cursor() as q:
    q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s FOR UPDATE',(RID,))
    before=q.fetchone()[0]
    if all(before[k]==v for k,v in fields.items()):print('Already corrected; no write');return
    assert before['functional_record_id']=='HH-7574890659'
    assert before['geo_lowest_level_value_id'] is None and before['geo_code_hierarchy_json'] is None
    assert before['address_line_2']==original['payload']['address_line_2']
    receipt={'action':'USER_AUTHORIZED_LOCATION_MAPPING_REPAIR','at':timestamp,'internal_record_id':RID,'source_sha256':original['source_sha256'],'mapping_version':mapped['mapping_version'],'before':before,'changes':fields,'status':'PREPARED','notes':'Only current geographic fields repaired. Original ODK source, intake and approval history retained. No GPS or ward IDs inferred.'}
    if path.exists():
     previous=json.loads(path.read_text())
     assert previous['status']=='PREPARED' and previous['before']==before
    else:
     with path.open('x') as out:json.dump(receipt,out,indent=2)
    q.execute("UPDATE g2p_register_households SET geo_lowest_level_value_id=%s,geo_code_hierarchy_json=%s::jsonb WHERE internal_record_id=%s AND geo_lowest_level_value_id IS NULL AND (geo_code_hierarchy_json IS NULL OR geo_code_hierarchy_json='null'::jsonb)",(fields['geo_lowest_level_value_id'],json.dumps(fields['geo_code_hierarchy_json']),RID))
    assert q.rowcount==1
    q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(RID,))
    after=q.fetchone()[0]
    assert {k:v for k,v in before.items() if k not in fields}=={k:v for k,v in after.items() if k not in fields}
  receipt['status']='COMMITTED';receipt['after']=after
  path.write_text(json.dumps(receipt,indent=2))
  r.execute('INSERT INTO audit(actor,action,reference,at) VALUES(?,?,?,?)',('user-authorized-maintenance','household_location_mapping_repaired',json.dumps({'household':RID,'receipt':str(path),'geo_id':fields['geo_lowest_level_value_id']}),timestamp))
 print(json.dumps({'household':'HH-7574890659','changes':fields,'receipt':str(path)}))
if __name__=='__main__':main()
