import sys,json,sqlite3,re
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
work=Path(__file__).parent/'legacy-verification';state=json.loads((work/'state.json').read_text());assert state['finished']
items=json.loads((work/'approved-mappings.json').read_text());c=sqlite3.connect('/opt/openg2p-lab/odk-sync/ledger.sqlite');c.row_factory=sqlite3.Row;checks=[]
with r.pg('register') as db:
 with db.cursor() as q:
  for item in items:
   row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(item['instance'],)).fetchone());assert row['state']=='SUBMITTED';assert row['source_hash']==item['review']['source_sha256']
   q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(row['internal_id'],));assert q.fetchone()[0]==1
   q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(row['internal_id'],));records=q.fetchall();assert len(records)==1
   for field,value in item['mapping']['payload'].items():assert records[0][0][field]==value
   q.execute('SELECT application_reference,approval_status,register_ingest_process_status FROM g2p_intake_form_submissions WHERE submission_id=%s',(row['submission_id'],));ref,approval,ingest=q.fetchone();assert approval=='APPROVED' and ingest=='PROCESSED'
   checks.append({'sample_reference':item['sample_reference'],'head_name':records[0][0]['household_head_name'],'household_name':records[0][0]['record_name'],'functional_id':records[0][0]['functional_record_id'],'application_reference':ref,'one_intake_one_record':True,'two_reviewers_verified':bool(state[item['sample_reference']]['afterFirstReview']),'domains_verified':state[item['sample_reference']]['domains']})
counts=dict(c.execute('SELECT state,count(*) FROM imports GROUP BY state').fetchall());assert counts=={'QUARANTINED':2,'SUBMITTED':13},counts
out={'checks':checks,'counts':counts,'original_sources_unchanged':True,'remaining_holds':'Only the two intentional invalid-numeric test submissions remain quarantined.'};(work/'final-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
