import json,uuid,time
from pathlib import Path
from test_meeting_native_workflow import call,REG,FORM,decide,detail,wait_for,master
from test_mbr_db_connection import connect
OUT=Path(__file__).parent.parent/'output/ooru-meeting-audit/verification';STATE=OUT/'household-parity-location-test.json';state=json.loads(STATE.read_text()) if STATE.exists() else {'checks':[]}
def save():STATE.write_text(json.dumps(state,indent=2))
def check(text):state['checks'].append(text);save();print('PASS',text,flush=True)
if not state.get('id'):
 state['internal_id']=str(uuid.uuid4());save()
 payload={'internal_record_id':state['internal_id'],'record_name':'Meeting Verification Household Location Parity','household_head_name':'Fictional Survey Head','sponsor_name':'NG CARES','respondent_name':'Fictional Respondent','enumerator_name':'SAMPLE: Amina Bello (Kaduna)','consent_status':'YES','household_heads_count':1,'head_list_complete':'YES','registration_confirmed':'YES','latitude':9.0765,'longitude':7.3986,'location_accuracy_m':12,'location_captured_at':'2026-11-12T19:00:00Z','location_capture_source':'Fictional browser location verification','geo_lowest_level_value_id':'NG001001_eziama','edit_action':'ADD'}
 result,_=call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':None,'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship','section_register_id':REG,'section_payload':[payload]});state['id']=result['submission_id'];save()
def section(sid,values,reg=REG):
 payload={'internal_record_id':state['internal_id'] if reg==REG else state['member_id'],'edit_action':'UPDATE' if reg==REG else 'ADD',**values}
 result,_=call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':state['id'],'form_id':FORM,'register_id':REG,'section_id':sid,'section_register_id':reg,'section_payload':[payload]});return result
if not state.get('finalized'):
 state.setdefault('member_id',str(uuid.uuid4()));save()
 member={'first_name':'Fictional','last_name':'Survey Head','gender':'MALE','estimated_age':35,'relationship_to_head':'SELF','contact_phone':'08000000000','nin_status':'NO','work_activity':'Fishing','highest_education':'Senior secondary','school_enrolled':'NO','healthcare_facility_use':'YES','severe_disability':'NO','social_group_member':'YES','bank_account_number':'123','link_internal_record_id':state['internal_id']}
 section('hh_members',member,'a0000000-0000-4000-8000-000000000001');bad,status=call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':state['id']},expect=False);assert status>=400 or bad.get('error');check('Server rejects malformed bank account before review')
 member['bank_account_number']='0000000000';member['bvn']='00000000000';section('hh_members',member,'a0000000-0000-4000-8000-000000000001')
 section('hh_survey_consent',{'survey_serial_number':'SAMPLE-PARITY-001','address_line_1':'Fictional verification address','latitude':9.0,'longitude':7.0})
 section('hh_income_shocks',{'income_source':'Fishing','monthly_household_income':1000,'major_shock_experienced':'YES','shock_types':['Flood','Fire']})
 section('hh_health_insurance',{'health_insurance_status':'YES'})
 section('hh_possessions',{'owns_assets':'YES','owns_television':'YES','television_count':2,'owns_generator':'YES','generator_count':1,'owns_computer':'YES'})
 section('hh_crops',{'grows_crops':'YES','crops_grown':['Maize','Cassava']})
 with connect() as c:
  with c.cursor() as q:
   q.execute('SELECT sponsor_name,survey_serial_number,shock_types,crops_grown,television_count,health_insurance_status FROM g2p_intake_form_households WHERE submission_id=%s',(state['id'],));row=q.fetchone();assert row==('NG CARES','SAMPLE-PARITY-001',['Flood','Fire'],['Maize','Cassava'],2,'YES'),row
 check('All survey sections merge into the same native household without losing earlier values')
 call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':state['id']});state['finalized']=True;save();check('Full household survey enters native two-stage approval')
if not state.get('l1'):
 decide(state,'abutu@gmail.com','approve','Fictional full survey parity check');wait_for(lambda:len(__import__('test_meeting_native_workflow').tasks(state))>=2,'L2 task');assert not master(state);state['l1']=True;save();check('First reviewer cannot publish household')
if not state.get('l2'):
 decide(state,'adaku@gmail.com','approve','Fictional survey publication verified',stage=2);wait_for(lambda:master(state),'Native publication');state['l2']=True;save()
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT shock_types,crops_grown,television_count,survey_serial_number FROM g2p_register_households WHERE internal_record_id=%s',(state['internal_id'],));assert q.fetchone()==(['Flood','Fire'],['Maize','Cassava'],2,'SAMPLE-PARITY-001')
  q.execute('SELECT bank_account_number,work_activity,highest_education,healthcare_facility_use FROM g2p_register_individuals WHERE internal_record_id=%s',(state['member_id'],));assert q.fetchone()==('0000000000','Fishing','Senior secondary','YES')
check('Final approval publishes household, crops, assets and enriched member fields to native master records')
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT latitude,longitude,location_accuracy_m,location_captured_at,geo_lowest_level_value_id FROM g2p_register_households WHERE internal_record_id=%s',(state['internal_id'],));row=q.fetchone();assert float(row[0])==9.0 and float(row[1])==7.0 and float(row[2])==12 and row[3]=='2026-11-12T19:00:00Z' and row[4]=='NG001001_eziama'
check('Final approval preserves submitted coordinates, accuracy, device time and selected ward in master registry')

state['status']='passed';save()
