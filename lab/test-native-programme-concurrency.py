"""Six simultaneous native PBMS reads; not six concurrent full processing workflows."""
import concurrent.futures,json,sys,time,datetime as dt
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
pb=r.Odoo('pbms-odoo','pbmsdb');ids=pb.call('g2p.program.definition','search',[[['program_status','=','ACTIVE']]],{'limit':6});assert len(ids)==6
def read(pid):
 start=time.perf_counter();client=r.Odoo('pbms-odoo','pbmsdb')
 row=client.call('g2p.program.definition','read',[[pid]],{'fields':['program_status','target_registry']})[0]
 return {'programme_id':pid,'active':row['program_status']=='ACTIVE','seconds':round(time.perf_counter()-start,3)}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(read,ids))
report={'scope':'Six concurrent native PBMS programme read requests','checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'requests':results,'status':'passed' if all(x['active'] for x in results) else 'failed','limitation':'Full concurrent eligibility enrolment conditionality and disbursement workflows remain to be load tested.'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-programme-concurrency.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
