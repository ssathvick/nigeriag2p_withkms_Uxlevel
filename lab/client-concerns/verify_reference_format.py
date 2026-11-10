import sys,json,uuid,re
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/odk-sync');from odk_sync_worker import Client,ROOT,REG,FORM
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as app
client=Client(json.loads((ROOT/'config.json').read_text()));created=[];refs=[]
try:
 for i in range(3):
  result=client.post('/intake-form-data/save_intake_form_submission',{'submission_id':None,'section_id':'hh_composition_headship','section_register_id':REG,'register_id':REG,'form_id':FORM,'section_payload':[{'internal_record_id':str(uuid.uuid4()),'record_name':'Synthetic reference-format probe '+str(i),'household_head_name':'Synthetic probe','size_total':1,'country_code':'NGA','record_status':'ACTIVE','edit_action':'ADD','link_internal_record_id':''}]})
  sid=result['submission_id'];created.append(sid)
  with app.pg('register') as db:
   with db.cursor() as q:q.execute('SELECT application_reference,draft_status,awe_request_id FROM g2p_intake_form_submissions WHERE submission_id=%s',(sid,));ref,status,awe=q.fetchone()
  assert status=='DRAFT' and awe is None;assert re.fullmatch(r'\d{4}[A-Z]{3}\d{2}-[A-Z0-9]{12}',ref),ref;refs.append(ref)
 assert len(set(refs))==3
finally:
 for sid in created:client.post('/intake-form-data/delete_intake_form_submission',{'submission_id':sid,'register_id':REG,'form_id':FORM})
 client.close()
with app.pg('register') as db:
 with db.cursor() as q:
  for sid in created:q.execute('SELECT count(*) FROM g2p_intake_form_submissions WHERE submission_id=%s',(sid,));assert q.fetchone()[0]==0
out={'three_unique_new_format_references':refs,'test_drafts_deleted':True,'approval_requests_created':0};(Path(__file__).parent/'legacy-verification/reference-format-test.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
