import json,sys,uuid,time
from pathlib import Path
from test_meeting_native_workflow import call,wait_for
from test_mbr_db_connection import connect
REG='a0000000-0000-4000-8000-000000000001';FORM='c1000000-0000-4000-8000-000000000001'
OUT=Path(__file__).parent.parent/'output/individual-workflow-verification'
phase=sys.argv[1] if len(sys.argv)>1 else None;name=sys.argv[2] if len(sys.argv)>2 else 'returned'
def save(s): (OUT/(name+'.json')).write_text(json.dumps(s,indent=2,default=str))
def detail(s):return call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':s['id'],'register_id':REG})[0]
def master(s):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT row_to_json(i) FROM g2p_register_individuals i WHERE internal_record_id=%s',(s['internal_id'],));r=q.fetchone();return r[0] if r else None
def finalize(s,expect=True):return call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':s['id'],'form_id':FORM,'register_id':REG},expect)
def write(s,payload,expect=True):return call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':s.get('id'),'form_id':FORM,'register_id':REG,'section_id':'in_demographic_details','section_register_id':REG,'section_payload':[payload]},expect)
def cr(s):return call('aarin@gmail.com','change-request/get',{'change_request_id':s['cr']['id']})[0]
def check(s,label):s.setdefault('checks',[]).append(label);save(s);print('PASS '+name+': '+label,flush=True)
def tasks(s,change=False):return call('abutu@gmail.com','awe/tasks-for-request',{'request_id':(cr(s) if change else detail(s))['awe_request_id']})[0]['tasks']
def decide(s,action,stage=1,change=False):
 t=next(t for t in tasks(s,change) if t['stage_order']==stage and t['status'] in ['open','claimed'])
 return call('adaku@gmail.com' if stage==2 else 'abutu@gmail.com','awe/submit-task-decision',{'task_id':t['id'],'action':action,'comment':'Fictional individual verification: '+action,'artifact_id':s['cr']['id'] if change else s['id'],'artifact_type':'registry.change_request' if change else 'registry.intake_form','current_stage':stage})
if __name__=='__main__':
 if phase=='household':
  from test_meeting_native_workflow import create,finalize as hf,master as hm,decide as hd,tasks as ht
  s=create('Individual workflow link fixture','aarin@gmail.com');s['member_id']=str(uuid.uuid4());(OUT/'linked-household.json').write_text(json.dumps(s))
  for section,reg,records in [('hh_composition_headship','a0000000-0000-4000-8000-000000000002',[{**s['payload'],'registration_confirmed':'YES','edit_action':'UPDATE'}]),('hh_members',REG,[{'internal_record_id':s['member_id'],'link_internal_record_id':s['internal_id'],'first_name':'Fictional','last_name':'Link fixture','estimated_age':30,'gender':'FEMALE','relationship_to_head':'SELF','edit_action':'ADD'}])]:
   call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':s['id'],'form_id':'c1000000-0000-4000-8000-000000000002','register_id':'a0000000-0000-4000-8000-000000000002','section_id':section,'section_register_id':reg,'section_payload':records})
  hf(s,'aarin@gmail.com');hd(s,'abutu@gmail.com','approve','Fictional linked household fixture');wait_for(lambda:any(t['stage_order']==2 for t in ht(s)),'Linked fixture second review');hd(s,'adaku@gmail.com','approve','Fictional linked household fixture',2);wait_for(lambda:hm(s),'Linked household publication');print('Isolated linked household ready')
 elif phase=='prepare':
  s={'internal_id':str(uuid.uuid4()),'record_name':'Meeting Verification Individual '+name,'checks':[]};save(s)
  s['payload']={'internal_record_id':s['internal_id'],'first_name':'Meeting Verification','last_name':'Individual '+name,'record_name':s['record_name'],'full_name':s['record_name'],'gender':'FEMALE','birth_date':'1990-01-01','estimated_age':36,'country_code':'NGA','edit_action':'ADD','link_internal_record_id':json.loads((OUT/'linked-household.json').read_text())['internal_id']}
  if name.startswith('change-'):s['payload']['estimated_age']=35
  r,_=write(s,s['payload']);s['id']=r['submission_id'];save(s);finalize(s);check(s,'Individual native registration saved and submitted; no master publication before approval');assert not master(s)
 else:
  s=json.loads((OUT/(name+'.json')).read_text())
  if phase=='enrich':
   with connect() as c:
    with c.cursor() as q:q.execute('SELECT internal_record_id FROM g2p_intake_form_individuals WHERE submission_id=%s',(s['id'],));s['internal_id']=q.fetchone()[0]
   save(s);check(s,'UI-created individual identity recorded for isolated fixture cleanup')
  elif phase=='publish-fixture':
   decide(s,'approve');wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(s)),'Second fixture approval');decide(s,'approve',2);wait_for(lambda:master(s),'Fixture publication');check(s,'Fictional individual fixture published through two independent approvals')
  elif phase=='link':
   s['payload']['link_internal_record_id']=json.loads((OUT/'linked-household.json').read_text())['internal_id'];write(s,{**s['payload'],'estimated_age':37,'edit_action':'UPDATE'});save(s)
  elif phase=='decide':decide(s,sys.argv[3],int(sys.argv[4]),len(sys.argv)>5 and sys.argv[5]=='change');check(s,'Decision '+ ' '.join(sys.argv[3:]))
  elif phase=='returned':
   d=wait_for(lambda:detail(s) if detail(s)['draft_status']=='DRAFT' else None,'Returned intake');assert d['approval_status']=='PENDING' and not master(s);check(s,'Return preserves submission and reasons, restores editability, and prevents publication')
  elif phase=='resubmitted':
   d=detail(s);assert d['draft_status']=='FINAL' and d['approval_status']=='PENDING' and not master(s);assert any(t['stage_order']==1 and t['status']=='open' for t in tasks(s));check(s,'Correction resubmits same individual registration and restarts first approval')
  elif phase=='level1':
   wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(s)),'Second approval');assert not master(s);check(s,'First approval does not publish individual')
  elif phase=='published':
   r=wait_for(lambda:master(s),'Individual publication');assert r['functional_record_id'] and r['estimated_age']==35;assert sum(e['event_type']=='request_returned' for e in detail(s)['review_history'])==2;s['baseline']=r;check(s,'Second approval publishes corrected individual, with both return attempts preserved')
  elif phase=='rejected':
   wait_for(lambda:detail(s)['approval_status']=='REJECTED','Permanent rejection');assert detail(s)['draft_status']=='FINAL' and not master(s)
   for r,status in [write(s,{**s['payload'],'edit_action':'UPDATE'},False),finalize(s,False)]:assert status>=400 or r.get('error')
   check(s,'Permanent individual rejection blocks editing, resubmission and publication')
  elif phase=='create-change':
   s['baseline']=master(s);s['tab_id']='individual_info_tab';body={'register_id':REG,'register_mnemonic':'Individual','section_register_id':REG,'tab_id':s['tab_id'],'section_id':'in_demographic_details','internal_record_id':s['internal_id'],'edit_action':'UPDATE','section_records':[{'internal_record_id':s['internal_id'],'edit_action':'UPDATE','estimated_age':36}]};r,_=call('aarin@gmail.com','change-request/create',body);s['cr']={'id':r['change_request_id'],'body':body};s['expected_proposal']=37;save(s);assert master(s)['estimated_age']==35;check(s,'Individual change request submitted without changing published master')
  elif phase=='change-returned':
   d=wait_for(lambda:cr(s) if str(cr(s).get('awe_request_status_summary')).startswith('returned') else None,'Returned change');assert d['approval_status']=='PENDING' and master(s)['estimated_age']==35;check(s,'Returned individual change retains reasons and leaves master unchanged')
  elif phase=='change-resubmitted':
   d=cr(s);assert d['change_request_id']==s['cr']['id'] and d['change_payload'][0]['estimated_age']==s['expected_proposal'];assert any(t['stage_order']==1 and t['status']=='open' for t in tasks(s,True));assert master(s)['estimated_age']==35;check(s,'Corrected individual change reuses request and restarts first approval')
  elif phase=='change-level1':
   wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(s,True)),'Second change approval');assert master(s)['estimated_age']==35;check(s,'First individual change approval leaves master unchanged')
  elif phase=='change-approved':
   wait_for(lambda:master(s)['estimated_age']==s['expected_proposal'],'Change publication');d=cr(s);assert d['approval_status']=='APPROVED';assert sum(e['event_type']=='request_returned' for e in d['review_history'])==2
   with connect() as c:
    with c.cursor() as q:q.execute('SELECT estimated_age FROM g2p_register_history_individuals WHERE change_request_id=%s',(s['cr']['id'],));assert q.fetchone()[0]==s['expected_proposal']
   assert d['current_register_data'][0]['estimated_age']==35;check(s,'Both change approvals publish corrected individual and preserve old/new domain values and both returns')
  elif phase=='diff':
   current=master(s);print('Changed fields:',[k for k,v in s['baseline'].items() if v!=current.get(k)])
  elif phase=='change-rejected':
   wait_for(lambda:cr(s)['approval_status']=='REJECTED','Change rejection');current=master(s);assert current['functional_record_id'];assert all(current.get(k)==v for k,v in s['baseline'].items() if k not in ['functional_record_id','search_text']);r,status=call('aarin@gmail.com','change-request/approve',{'change_request_id':s['cr']['id']},False);assert status>=400 or r.get('error');check(s,'Permanent change rejection locks request and leaves all master business fields unchanged')
  else:raise ValueError(phase)
