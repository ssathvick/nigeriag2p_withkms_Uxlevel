import json,uuid
from pathlib import Path
from test_meeting_native_workflow import call,REG,FORM
out=Path(__file__).parent.parent/'output/ooru-meeting-audit/verification/enumeration-sample.json'
if out.exists():
 print(json.dumps({'status':'exists','sample':json.loads(out.read_text())['submission_id']}))
else:
 payload={'internal_record_id':str(uuid.uuid4()),'record_name':'SAMPLE — Household enumeration walkthrough','household_head_name':'Sample Household Head','size_total':1,'country_code':'NGA','sponsor_name':'NG CARES','consent_status':'YES','respondent_name':'Sample Respondent','enumerator_name':'SAMPLE: Amina Bello (Kaduna)','survey_community':'Sample community — not a real household','edit_action':'ADD','link_internal_record_id':''}
 body,status=call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':None,'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship','section_register_id':REG,'section_payload':[payload]})
 detail,_=call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':body['submission_id'],'register_id':REG})
 assert detail['draft_status']=='DRAFT'
 out.write_text(json.dumps({'submission_id':body['submission_id'],'internal_record_id':payload['internal_record_id'],'status':'DRAFT','sample':True},indent=2));print(json.dumps({'status':'passed','sampleDraft':body['submission_id'],'submitted':False,'masterPublished':False}))
