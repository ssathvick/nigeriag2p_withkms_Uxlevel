import json,uuid,sys
from pathlib import Path
from test_meeting_native_workflow import call,wait_for
from test_mbr_db_connection import connect
OUT=Path(__file__).parent.parent/'output/unified-workspace-verification';OUT.mkdir(exist_ok=True)
HH='a0000000-0000-4000-8000-000000000002';IND='a0000000-0000-4000-8000-000000000001'
def save(n,s):(OUT/(n+'.json')).write_text(json.dumps(s,default=str,indent=2))
def load(n):return json.loads((OUT/(n+'.json')).read_text())
def detail(s):return call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':s['id'],'register_id':s['reg']})[0]
def master(s):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT functional_record_id FROM '+('g2p_register_households' if s['type']=='household' else 'g2p_register_individuals')+' WHERE internal_record_id=%s',(s['internal_id'],));r=q.fetchone();return r and r[0]
def create(n,kind,payload):
 reg=HH if kind=='household' else IND;form='c1000000-0000-4000-8000-00000000000'+('2' if kind=='household' else '1');s={'type':kind,'reg':reg,'form':form,'internal_id':str(uuid.uuid4()),'record_name':'Meeting Verification Unified '+kind,'checks':[]};save(n,s)
 data={'internal_record_id':s['internal_id'],'record_name':s['record_name'],'country_code':'NGA','edit_action':'ADD',**payload};r,_=call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':None,'form_id':form,'register_id':reg,'section_id':'hh_composition_headship' if kind=='household' else 'in_demographic_details','section_register_id':reg,'section_payload':[data]});s['id']=r['submission_id'];save(n,s);return s
def finalize(s):call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':s['id'],'form_id':s['form'],'register_id':s['reg']})
def change(n,s):
 tab='household_housing_services_tab' if s['type']=='household' else 'individual_info_tab';section='hh_dwelling_services' if s['type']=='household' else 'in_demographic_details';field='rooms_count' if s['type']=='household' else 'estimated_age';s.update(tab_id=tab,section_id=section,field=field)
 r,_=call('aarin@gmail.com','change-request/create',{'register_id':s['reg'],'register_mnemonic':s['type'].capitalize(),'section_register_id':s['reg'],'tab_id':tab,'section_id':section,'internal_record_id':s['internal_id'],'edit_action':'UPDATE','section_records':[{'internal_record_id':s['internal_id'],'edit_action':'UPDATE',field:3 if field=='rooms_count' else 37}]});s['cr']={'id':r['change_request_id']};save(n,s)
phase=sys.argv[1]
if phase=='household':
 s=create('household','household',{'household_head_name':'Fictional UX Head','size_total':1,'sponsor_name':'NSIPA','consent_status':'YES','respondent_name':'Fictional UX Head','enumerator_name':'aarin@gmail.com','registration_confirmed':'YES','rooms_count':2});s['member_id']=str(uuid.uuid4());save('household',s)
 call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':s['id'],'form_id':s['form'],'register_id':HH,'section_id':'hh_members','section_register_id':IND,'section_payload':[{'internal_record_id':s['member_id'],'link_internal_record_id':s['internal_id'],'first_name':'Fictional','last_name':'UX Head','gender':'FEMALE','relationship_to_head':'SELF','estimated_age':36,'edit_action':'ADD'}]});finalize(s);print('Fictional household submitted')
elif phase=='individual':
 h=load('household');wait_for(lambda:master(h),'Household publication');s=create('individual','individual',{'first_name':'Meeting Verification','last_name':'Unified individual','full_name':'Meeting Verification Unified individual','estimated_age':36,'gender':'FEMALE','link_internal_record_id':h['internal_id']});finalize(s);change('household',h);print('Fictional individual submitted and household change proposed')
elif phase=='individual-change':
 s=load('individual');wait_for(lambda:master(s),'Individual publication');change('individual',s);print('Fictional individual change proposed')
elif phase=='verify':
 for name in ['household','individual']:
  s=load(name);wait_for(lambda:master(s),'Publication');assert detail(s)['approval_status']=='APPROVED';d=call('aarin@gmail.com','change-request/get',{'change_request_id':s['cr']['id']})[0];assert d['approval_status']=='APPROVED';s['checks']=['Registration approved through both UI approval levels','Change request approved through both UI approval levels'];save(name,s)
 print('Both fictional registrations and change requests passed two UI approval levels')
