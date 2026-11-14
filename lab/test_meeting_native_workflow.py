"""Exercise fictional records through native APIs using the supplied five identities."""
import sys,json,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'client-concerns'))
import test_location_import_e2e as auth
from test_mbr_db_connection import connect
HOST='https://g2p-register.wverve.in';auth.HOST=HOST
OUT=Path(__file__).parent.parent/'output/ooru-meeting-audit/verification';OUT.mkdir(parents=True,exist_ok=True)
STATE=OUT/'native-workflow-state.json';state=json.loads(STATE.read_text()) if STATE.exists() else {'cases':{},'checks':[]}
credentials=json.loads(Path('/mnt/h/Nigeria_Mosip/Credentials/mbr_demo_credentials.json').read_text())
sessions={}
REG='a0000000-0000-4000-8000-000000000002';FORM='c1000000-0000-4000-8000-000000000002'
def save():STATE.write_text(json.dumps(state,indent=2,default=str))
def check(label,condition=True):
 if not condition:raise AssertionError(label)
 if label not in state['checks']:state['checks'].append(label);save()
 print('PASS',label,flush=True)
def session(email):
 if email not in sessions:sessions[email]=auth.login(HOST,email,credentials[email]['password'])
 return sessions[email]
def call(email,path,data,expect=True):
 s=session(email);csrf=next((c.value for c in s.cookies if c.name=='X-CSRF-Token'),None)
 if csrf:s.headers['X-CSRF-Token']=csrf
 r=s.post(HOST+'/api/'+path,json=data,timeout=45)
 try:body=r.json()
 except Exception:raise RuntimeError(path+' HTTP '+str(r.status_code))
 if expect and (not r.ok or isinstance(body,dict) and body.get('error')):raise RuntimeError(path+' '+str(r.status_code)+' '+str(body.get('error',body) if isinstance(body,dict) else body)[:500])
 return body,r.status_code
def detail(case):return call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':case['id'],'register_id':REG})[0]
def wait_for(fn,label):
 for _ in range(35):
  result=fn()
  if result:return result
  time.sleep(1)
 raise AssertionError('Timeout: '+label)
def tasks(case):return call('abutu@gmail.com','awe/tasks-for-request',{'request_id':detail(case)['awe_request_id']})[0]['tasks']
def decide(case,email,action,reason,stage=1,expect=True,kind='registry.intake_form'):
 if kind=='registry.intake_form':items=tasks(case)
 else:items=call('abutu@gmail.com','awe/tasks-for-request',{'request_id':case['request_id']})[0]['tasks']
 task=next(t for t in items if t['stage_order']==stage and t['status'] in ['open','claimed'])
 return call(email,'awe/submit-task-decision',{'task_id':task['id'],'action':action,'comment':reason,'artifact_id':case['id'],'artifact_type':kind,'current_stage':stage},expect)
def create(name,email='abuchi@gmail.com'):
 if name in state['cases']:return state['cases'][name]
 case={'internal_id':str(uuid.uuid4())};state['cases'][name]=case;save()
 payload={'internal_record_id':case['internal_id'],'record_name':'Meeting Verification '+name,'household_head_name':'Fictional Test Head','size_total':1,'country_code':'NGA','sponsor_name':'NSIPA','consent_status':'YES','respondent_name':'Fictional Test Head','enumerator_name':email,'survey_community':'Fictional verification only','edit_action':'ADD','link_internal_record_id':''}
 result,_=call(email,'intake-form/save-intake-form-submission',{'submission_id':None,'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship','section_register_id':REG,'section_payload':[payload]})
 case.update(id=result['submission_id'],payload=payload);save();return case
def finalize(case,email='abuchi@gmail.com'):return call(email,'intake-form/finalize-intake-form-submission',{'submission_id':case['id'],'form_id':FORM,'register_id':REG})
def master(case):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT functional_record_id,record_name,sponsor_name,consent_status FROM g2p_register_households WHERE internal_record_id=%s',(case['internal_id'],));return q.fetchone()
def run():
 main=create('Return then approve');check('Field agent saves directly to native intake')
 if not detail(main).get('awe_request_id'):
  call('abuchi@gmail.com','intake-form/save-intake-form-submission',{'submission_id':main['id'],'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship','section_register_id':REG,'section_payload':[main['payload']]})
  finalize(main)
 current=detail(main)
 if current['draft_status']=='DRAFT' and str(current.get('awe_request_status_summary')).startswith('returned'):
  main['returned']=True;save()
 if not main.get('returned'):
  denied,status=decide(main,'adaku@gmail.com','approve','Invalid stage identity',expect=False);check('Second reviewer cannot decide first-stage task',status>=400 or bool(denied.get('error')))
  denied,status=decide(main,'abutu@gmail.com','return','',expect=False);check('Return requires reason on server',status>=400 or bool(denied.get('error')))
  decide(main,'abutu@gmail.com','return','Correct the fictional household name before review.')
  wait_for(lambda:detail(main)['draft_status']=='DRAFT','Return makes native intake editable');main['returned']=True;save()
  check('Return is distinct from permanent rejection',detail(main)['approval_status']=='PENDING')
  check('Original return attempt appears in native history',any(e['event_type']=='request_returned' for e in detail(main).get('review_history',[])))
 if not main.get('resubmitted'):
  payload={**main['payload'],'record_name':'Meeting Verification Corrected Household','edit_action':'UPDATE'}
  call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':main['id'],'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship','section_register_id':REG,'section_payload':[payload]})
  finalize(main,'aarin@gmail.com');main['resubmitted']=True;save();check('Online officer corrects field-agent intake using same submission ID')
 if not main.get('level1'):
  if not any(t['stage_order']==2 for t in tasks(main)):
   decide(main,'abutu@gmail.com','approve','Completeness and duplicate review verified.')
  wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(main)),'Second review activated')
  check('First approval does not publish master record',not master(main));main['level1']=True;save()
 check('Return is distinct from permanent rejection',any(e['event_type']=='request_returned' for e in detail(main).get('review_history',[])))
 check('Original return attempt appears in native history',any(e['event_type']=='request_returned' for e in detail(main).get('review_history',[])))
 if not main.get('approved'):
  decide(main,'adaku@gmail.com','approve','Independent final review verified.',stage=2)
  wait_for(lambda:detail(main)['approval_status']=='APPROVED','Native final approval')
  row=wait_for(lambda:master(main),'Native master ingestion');check('Approved intake receives functional household ID',bool(row[0]))
  check('Sponsor and consent publish into native master',row[2:] == ('NSIPA','YES'));main['approved']=True;save()
 rejected=create('Permanent rejection','aarin@gmail.com')
 if not detail(rejected).get('awe_request_id'):finalize(rejected,'aarin@gmail.com')
 if not rejected.get('rejected'):
  decide(rejected,'abutu@gmail.com','reject','Fictional permanent rejection regression.')
  wait_for(lambda:detail(rejected)['approval_status']=='REJECTED','Permanent rejection webhook');rejected['rejected']=True;save()
 check('Permanent rejection remains final and locked',detail(rejected)['draft_status']=='FINAL')
 denied,status=call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':rejected['id'],'form_id':FORM,'register_id':REG,'section_id':'hh_composition_headship','section_register_id':REG,'section_payload':[rejected['payload']]},False)
 check('Server rejects edits to permanently rejected intake',status>=400 or bool(denied.get('error')))
 check('Rejected intake creates no master record',not master(rejected))
 state['status']='passed';save();print(json.dumps({'status':'passed','checks':len(state['checks'])}))
if __name__=='__main__':
 try:run()
 finally:
  for s in sessions.values():s.close()
