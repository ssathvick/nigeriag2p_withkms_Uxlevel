import json,uuid
from pathlib import Path
from test_meeting_native_workflow import call,REG,FORM
out=Path(__file__).parent.parent/'output/ooru-meeting-audit/verification';state={'internal_id':str(uuid.uuid4()),'member_id':str(uuid.uuid4()),'checks':[]}
h={'internal_record_id':state['internal_id'],'record_name':'Meeting Verification Survey Guards','household_head_name':'Fictional Guard Head','sponsor_name':'NSIPA','respondent_name':'Fictional Respondent','enumerator_name':'SAMPLE: Amina Bello (Kaduna)','consent_status':'YES','edit_action':'ADD'}
def save(sid,payload,reg=REG):
 result,_=call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':state.get('id'),'form_id':FORM,'register_id':REG,'section_id':sid,'section_register_id':reg,'section_payload':[payload]});state['id']=result['submission_id'];(out/'household-parity-guards.json').write_text(json.dumps(state,indent=2))
def rejects(part):
 body,status=call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':state['id']},False);assert status>=400 and part.lower() in str(body).lower(),body;state['checks'].append(part);print('PASS',part,flush=True)
save('hh_composition_headship',h);rejects('Confirm that the household records')
h.update(edit_action='UPDATE',registration_confirmed='YES');save('hh_survey_consent',h);rejects('at least one household member')
m={'internal_record_id':state['member_id'],'first_name':'Fictional','last_name':'Guard Head','gender':'MALE','estimated_age':35,'relationship_to_head':'SELF','link_internal_record_id':state['internal_id'],'nin_status':'YES','nin_id_type':'NIN','foundational_id':'0000000000','nin_confirmation':'0000000000','edit_action':'ADD'}
save('hh_members',m,'a0000000-0000-4000-8000-000000000001');rejects('11-digit NIN')
m.update(edit_action='UPDATE',foundational_id='00000000000',nin_confirmation='11111111111');save('hh_members',m,'a0000000-0000-4000-8000-000000000001');rejects('confirmation does not match')
m.update(nin_confirmation='00000000000',bank_account_number='123');save('hh_members',m,'a0000000-0000-4000-8000-000000000001');rejects('Bank account numbers')
m['bank_account_number']='0000000000';save('hh_members',m,'a0000000-0000-4000-8000-000000000001')
h.update(owns_assets='YES',owns_television='YES');save('hh_possessions',h);rejects('count for each television')
h.update(television_count='2',grows_crops='YES');save('hh_crops',h);rejects('Select the crops grown')
state['status']='passed';(out/'household-parity-guards.json').write_text(json.dumps(state,indent=2));print('All guard checks passed; fixture remains unsubmitted for cleanup')
