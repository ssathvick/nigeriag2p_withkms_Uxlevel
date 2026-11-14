import json,sys,uuid
from pathlib import Path
from test_meeting_native_workflow import call,wait_for
from test_mbr_db_connection import connect
OUT=Path(__file__).parent.parent/'output/release-workflow-verification'
phase,kind,name=sys.argv[1:4]
folder=OUT/kind;folder.mkdir(parents=True,exist_ok=True);file=folder/(name+'.json')
HH='a0000000-0000-4000-8000-000000000002';IND='a0000000-0000-4000-8000-000000000001'
REG=HH if kind=='household' else IND;FORM='c1000000-0000-4000-8000-00000000000'+('2' if kind=='household' else '1')
def save(s):file.write_text(json.dumps(s,indent=2,default=str))
def detail(s,change=False):return call('aarin@gmail.com','change-request/get' if change else 'intake-form/get-intake-form-submission',{'change_request_id':s['cr']['id']} if change else {'submission_id':s['id'],'register_id':REG})[0]
def master(s):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT row_to_json(r) FROM g2p_register_'+('households' if kind=='household' else 'individuals')+' r WHERE internal_record_id=%s',(s['internal_id'],));r=q.fetchone();return r[0] if r else None
def tasks(s,change=False):return call('abutu@gmail.com','awe/tasks-for-request',{'request_id':detail(s,change)['awe_request_id']})[0]['tasks']
def write(s,payload):return call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':s.get('id'),'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship' if kind=='household' else 'in_demographic_details','section_register_id':REG,'section_payload':[payload]})[0]
if phase=='prepare':
 if file.exists():raise RuntimeError('Tracked fixture already exists; use a fresh output folder rather than overwriting its identity')
 s={'type':kind,'reg':REG,'form':FORM,'internal_id':str(uuid.uuid4()),'record_name':'Meeting Verification Release '+kind+' '+name,'checks':[]};save(s)
 payload={'internal_record_id':s['internal_id'],'record_name':s['record_name'],'edit_action':'ADD','country_code':'NGA'}
 if kind=='household':payload.update(household_head_name='Fictional Release Head',size_total=1,sponsor_name='NSIPA',consent_status='YES',respondent_name='Fictional Release Head',enumerator_name='aarin@gmail.com',registration_confirmed='YES',rooms_count=2)
 else:payload.update(first_name='Meeting Verification',last_name='Release individual '+name,full_name=s['record_name'],estimated_age=36,gender='FEMALE',link_internal_record_id=json.loads((OUT/'household/returned.json').read_text())['internal_id'])
 s['payload']=payload;s['id']=write(s,payload)['submission_id'];save(s)
 if kind=='household':
  s['member_id']=str(uuid.uuid4());save(s)
  call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':s['id'],'form_id':FORM,'register_id':REG,'section_id':'hh_members','section_register_id':IND,'section_payload':[{'internal_record_id':s['member_id'],'link_internal_record_id':s['internal_id'],'first_name':'Fictional','last_name':'Release Head','estimated_age':36,'gender':'FEMALE','relationship_to_head':'SELF','edit_action':'ADD'}]})
 call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':s['id'],'form_id':FORM,'register_id':REG});assert not master(s)
else:
 s=json.loads((folder/'returned.json').read_text() if phase=='create-change' else file.read_text());change=phase.startswith('change-')
 if phase in ['returned','change-returned']:
  wait_for(lambda:str(detail(s,change).get('awe_request_status_summary')).startswith('returned'),'Return transition')
  if not change:assert detail(s)['draft_status']=='DRAFT' and not master(s)
  else:assert master(s)[s['field']]==s['baseline'][s['field']]
 elif phase in ['resubmitted','change-resubmitted','level1','change-level1']:
  stage=2 if phase.endswith('level1') else 1
  wait_for(lambda:any(t['stage_order']==stage and t['status']=='open' for t in tasks(s,change)),'Expected approval stage')
  if not change:assert not master(s)
  else:assert master(s)[s['field']]==s['baseline'][s['field']]
 elif phase=='published':
  r=wait_for(lambda:master(s) if master(s) and master(s).get('functional_record_id') else None,'Publication with functional ID');assert detail(s)['approval_status']=='APPROVED';assert sum(e['event_type']=='request_returned' for e in detail(s)['review_history'])==2
  assert r['survey_community']=='Fictional corrected second review' if kind=='household' else r['estimated_age']==35
 elif phase=='rejected':
  wait_for(lambda:detail(s)['approval_status']=='REJECTED','Rejection');assert not master(s) and detail(s)['draft_status']=='FINAL'
  for endpoint,body in [('intake-form/save-intake-form-submission',{'submission_id':s['id'],'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship' if kind=='household' else 'in_demographic_details','section_register_id':REG,'section_payload':[{**s['payload'],'edit_action':'UPDATE'}]}),('intake-form/finalize-intake-form-submission',{'submission_id':s['id'],'form_id':FORM,'register_id':REG})]:
   r,status=call('aarin@gmail.com',endpoint,body,False);assert status>=400 or r.get('error')
 elif phase=='create-change':
  if file.exists():raise RuntimeError('Tracked change fixture already exists; do not overwrite its identity')
  source=json.loads((folder/'returned.json').read_text());s=source.copy();s.pop('cr',None);s['baseline']=master(s);s['field']='rooms_count' if kind=='household' else 'estimated_age';s['tab_id']='household_housing_services_tab' if kind=='household' else 'individual_info_tab';s['section_id']='hh_dwelling_services' if kind=='household' else 'in_demographic_details';s['expected_proposal']=4 if kind=='household' else 37
  body={'register_id':REG,'register_mnemonic':kind.capitalize(),'section_register_id':REG,'tab_id':s['tab_id'],'section_id':s['section_id'],'internal_record_id':s['internal_id'],'edit_action':'UPDATE','section_records':[{'internal_record_id':s['internal_id'],'edit_action':'UPDATE',s['field']:3 if kind=='household' else 36}]}
  s['cr']={'id':call('aarin@gmail.com','change-request/create',body)[0]['change_request_id']};save(s)
 elif phase=='change-approved':
  wait_for(lambda:master(s)[s['field']]==s['expected_proposal'],'Approved change publication');assert detail(s,True)['approval_status']=='APPROVED';assert sum(e['event_type']=='request_returned' for e in detail(s,True)['review_history'])==2
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT '+s['field']+' FROM g2p_register_history_'+('households' if kind=='household' else 'individuals')+' WHERE change_request_id=%s',(s['cr']['id'],));assert q.fetchone()[0]==s['expected_proposal']
 elif phase=='change-rejected':
  wait_for(lambda:detail(s,True)['approval_status']=='REJECTED','Rejected change');assert all(master(s).get(k)==v for k,v in s['baseline'].items() if k not in ['functional_record_id','search_text'])
  r,status=call('aarin@gmail.com','change-request/approve',{'change_request_id':s['cr']['id']},False);assert status>=400 or r.get('error')
 elif phase=='correction2':s['correction_expected']='Fictional corrected second review' if kind=='household' else 35
 elif phase=='change-correction2':s['expected_proposal']=5 if kind=='household' else 36
 else:raise ValueError(phase)
s.setdefault('checks',[]).append(phase);save(s);print('PASS '+kind+' '+name+' '+phase,flush=True)
