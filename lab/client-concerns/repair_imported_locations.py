"""Audit/backfill current imported household geography from preserved ODK sources.

Default is read-only. --apply updates only missing fields, never conflicts or
historic intake/approval snapshots. Every batch has a private before/after receipt.
"""
import sys,json,hashlib,sqlite3,uuid,fcntl,os,datetime
from pathlib import Path
from collections import Counter
from odk_geography import load_geography,resolve_geography
from odk_household_mapping import parse_xml
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
ROOT=Path('/opt/openg2p-lab/odk-sync')
FIELDS=('geo_lowest_level_value_id','geo_code_hierarchy_json')

def expected(row,ledger,master):
 rid=row['internal_record_id'];folder=ROOT/'receipts'/rid
 receipt=json.loads((folder/'mapping.json').read_text())
 xml=(folder/'source.xml').read_bytes();digest=hashlib.sha256(xml).hexdigest()
 if digest!=receipt['source_sha256'] or digest!=ledger['source_hash']:raise ValueError('Source hash mismatch')
 node=parse_xml(xml);instance=node.findtext('meta/instanceID')
 if instance!=ledger['instance_id'] or node.get('id')!=ledger['form_id']:raise ValueError('Source identity mismatch')
 if str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-odk:'+node.get('id')+':'+instance))!=rid:raise ValueError('Deterministic household ID mismatch')
 if receipt['payload']['internal_record_id']!=rid:raise ValueError('Receipt household ID mismatch')
 if row['address_line_2']!=receipt['payload']['address_line_2']:raise ValueError('Address changed since import; manual review required')
 fields=resolve_geography(node.findtext('location/state') or '',node.findtext('location/lga') or '',master)
 for field in FIELDS:
  if row[field] is not None and row[field]!=fields[field]:
   # Equivalent hierarchy formats may include extra IDs/metadata.
   if field=='geo_code_hierarchy_json' and isinstance(row[field],dict):
    old=[(v.get('level_value_id'),v.get('level_value_mnemonic')) for v in row[field].get('hierarchy',[])]
    new=[(v['level_value_id'],v['level_value_mnemonic']) for v in fields[field]['hierarchy']]
    if old==new:continue
   raise ValueError('Existing geography conflicts with source; manual review required')
 return {k:v for k,v in fields.items() if row[k] is None},digest

def run(apply=False):
 os.umask(0o077)
 master=load_geography()
 with sqlite3.connect('file:'+str(ROOT/'ledger.sqlite')+'?mode=ro',uri=True) as ledgerdb:
  ledgerdb.row_factory=sqlite3.Row
  entries=[dict(x) for x in ledgerdb.execute('SELECT * FROM imports')]
 ledger={x['internal_id']:x for x in entries if x['internal_id']}
 report={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'apply':apply,'ledger_count':len(entries),'ledger_states':dict(Counter(x['state'] for x in entries)),'rows':[]}
 with open(ROOT/'worker.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  with r.pg('register') as c:
   if not apply:c.set_session(readonly=True)
   with c.cursor() as q:
    q.execute("SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=ANY(%s) OR created_by ILIKE '%%synchronization%%'"+(' FOR UPDATE' if apply else ''),(list(ledger),))
    households=[x[0] for x in q.fetchall()]
    present={x['internal_record_id'] for x in households}
    for row in households:
     rid=row['internal_record_id'];item={'id':rid,'functional_id':row['functional_record_id'],'name':row['record_name']}
     try:
      if rid not in ledger:raise ValueError('No matching import ledger entry')
      changes,digest=expected(row,ledger[rid],master)
      item.update(status='REPAIRABLE' if changes else 'ALREADY_COMPLETE',changes=changes,source_sha256=digest)
      if changes:item['before']=row
     except (ValueError,KeyError,OSError) as e:item.update(status='HELD',reason=str(e))
     report['rows'].append(item)
    report['not_in_current_registry']=[{'id':rid,'state':entry['state'],'submission_id':entry['submission_id']} for rid,entry in ledger.items() if rid not in present]
    if apply:
     path=ROOT/'receipts'/('location-batch-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
     report['receipt']=str(path);report['transaction']='PREPARED'
     path.write_text(json.dumps(report,indent=2))
     for item in report['rows']:
      if item['status']!='REPAIRABLE':continue
      changes=item['changes']
      assignments=[];params=[]
      for field,value in changes.items():
       assert field in FIELDS
       assignments.append(field+'=%s'+('::jsonb' if field.endswith('_json') else ''))
       params.append(json.dumps(value) if field.endswith('_json') else value)
      q.execute('UPDATE g2p_register_households SET '+','.join(assignments)+' WHERE internal_record_id=%s',(*params,item['id']))
      assert q.rowcount==1
      q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(item['id'],))
      after=q.fetchone()[0]
      assert all(after[k]==v for k,v in changes.items())
      assert {k:v for k,v in after.items() if k not in changes}=={k:v for k,v in item['before'].items() if k not in changes}
      item.update(status='REPAIRED',after=after)
  if apply:
   report['transaction']='COMMITTED';path.write_text(json.dumps(report,indent=2))
   r.execute('INSERT INTO audit(actor,action,reference,at) VALUES(?,?,?,?)',('user-authorized-maintenance','imported_household_location_batch_repair',str(path),report['at']))
 report['counts']=dict(Counter(x['status'] for x in report['rows']))
 output=Path(__file__).parent/('imported-location-repair-result.json' if apply else 'imported-location-audit.json')
 output.write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
 print(json.dumps([{k:x[k] for k in ['functional_id','status','reason'] if k in x} for x in report['rows']],indent=2))
if __name__=='__main__':run('--apply' in sys.argv)
