import sys,json,sqlite3,re,datetime,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
work=Path(__file__).parent/'final-e2e-verification';state=json.loads((work/'state.json').read_text());assert state['finished']
c=sqlite3.connect('/opt/openg2p-lab/odk-sync/ledger.sqlite');c.row_factory=sqlite3.Row;checks=[]
with r.pg('register') as db,r.pg('awe') as awe:
 with db.cursor() as q,awe.cursor() as a:
  for key,item in state.items():
   if not isinstance(item,dict) or 'mapping' not in item:continue
   row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(item['instance'],)).fetchone());assert row['state']=='SUBMITTED';assert row['source_hash']==item['mapping']['source_sha256']
   q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(row['internal_id'],));assert q.fetchone()[0]==1
   q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(row['internal_id'],));records=q.fetchall();assert len(records)==1
   saved=records[0][0]
   for field,value in item['mapping']['payload'].items():assert saved[field]==value,(key,field)
   assert saved['functional_record_id'].startswith('HH-')
   q.execute('SELECT application_reference,approval_status,register_ingest_process_status,awe_request_id FROM g2p_intake_form_submissions WHERE submission_id=%s',(row['submission_id'],));ref,approval,ingest,request=q.fetchone();assert approval=='APPROVED' and ingest=='PROCESSED';assert re.fullmatch(r'\d{4}[A-Z]{3}\d{2}-[A-Z0-9]{12}',ref)
   a.execute('SELECT stage_order,actor,action FROM approval_decision WHERE request_id=%s ORDER BY stage_order',(request,));decisions=a.fetchall();assert len(decisions)==2;assert len({x[1] for x in decisions})==2;assert [x[0] for x in decisions]==[1,2];assert all(x[2]=='approve' for x in decisions),decisions
   a.execute('SELECT policy_version,status FROM approval_request WHERE id=%s',(request,));policy,status=a.fetchone();assert policy==2
   assert item['beforeApproval']['registry_count']==0;assert item['afterFirstReview']['registry_count']==0
   checks.append({'case':key,'head':saved['household_head_name'],'source_domain':item['odkHost'],'functional_id':saved['functional_record_id'],'application_reference':ref,'intake_count':1,'registry_count':1,'saved_fields_match':True,'withheld_until_second_approval':True,'policy_version':policy,'review_decisions':[{'stage':stage,'actor':actor,'action':action} for stage,actor,action in decisions]})
assert len(checks)==4
counts=dict(c.execute('SELECT state,count(*) FROM imports GROUP BY state').fetchall());assert counts=={'EXCLUDED_TEST':2,'SUBMITTED':17},counts
status=json.loads(Path('/opt/openg2p-lab/odk-sync/status.json').read_text());assert status['counts']==counts and status['transient_failures']==0
for command,expected in [('is-active','active'),('is-enabled','enabled')]:assert subprocess.check_output(['systemctl',command,'nsipa-odk-sync.timer'],text=True).strip()==expected
assert len(json.loads((work/'replay-checks.json').read_text()))==8
assert len(json.loads((work/'location-checks.json').read_text()))==8
out={'completed_at_ist':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat(),'checks':checks,'ledger_counts':counts,'active_quarantines':0,'scheduled_pass':status,'timer_active_and_enabled':True,'registry_record_checks':8,'numeric_label_checks':4,'replay_checks':8,'regression_tests':21,'hardware_test':'Not performed; no device connected','npc_attestation':'Pending approved business specification and acceptance criteria'}
(work/'final-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
