import json,uuid
from pathlib import Path
from test_meeting_native_workflow import call
out=Path(__file__).parent.parent/'output/no-enumerator-verification';out.mkdir(exist_ok=True)
HH='a0000000-0000-4000-8000-000000000002';IND='a0000000-0000-4000-8000-000000000001';FORM='c1000000-0000-4000-8000-000000000002'
file=out/'household.json';assert not file.exists(),'Do not overwrite tracked fixture identities'
s={'type':'household','reg':HH,'form':FORM,'internal_id':str(uuid.uuid4()),'record_name':'Meeting Verification Without Enumerator','checks':[]};file.write_text(json.dumps(s))
payload={'internal_record_id':s['internal_id'],'record_name':s['record_name'],'household_head_name':'Fictional Enumerator Removal','size_total':1,'sponsor_name':'NSIPA','respondent_name':'Fictional Enumerator Removal','consent_status':'NO','registration_confirmed':'YES','edit_action':'ADD'}
def save():file.write_text(json.dumps(s,indent=2))
def write(p,section='hh_composition_headship',reg=HH):return call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':s.get('id'),'form_id':FORM,'register_id':HH,'section_id':section,'section_register_id':reg,'section_payload':[p]})[0]
s['id']=write(payload)['submission_id'];save();s['member_id']=str(uuid.uuid4());save()
write({'internal_record_id':s['member_id'],'link_internal_record_id':s['internal_id'],'first_name':'Fictional','last_name':'Enumerator Removal','gender':'FEMALE','estimated_age':36,'relationship_to_head':'SELF','edit_action':'ADD'},'hh_members',IND)
final={'submission_id':s['id'],'form_id':FORM,'register_id':HH}
r,status=call('aarin@gmail.com','intake-form/finalize-intake-form-submission',final,False);assert status>=400 or r.get('error');s['checks'].append('Informed consent still required');save()
write({**payload,'consent_status':'YES','edit_action':'UPDATE'});call('aarin@gmail.com','intake-form/finalize-intake-form-submission',final)
d=call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':s['id'],'register_id':HH})[0];assert d['draft_status']=='FINAL' and d['approval_status']=='PENDING' and d['awe_request_id'];s['checks'].append('Saved and submitted for approval without enumerator');save();print('PASS: no enumerator required; consent protection and approval routing retained')
