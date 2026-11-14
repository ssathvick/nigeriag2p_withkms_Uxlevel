import sys,json,uuid,time,xml.etree.ElementTree as E
from pathlib import Path
import yaml,requests
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
from test_meeting_native_workflow import call,REG,decide,tasks,master,wait_for
OUT=ROOT.parent/'output/household-change-verification';OUT.mkdir(exist_ok=True)
PRIVATE=Path('/opt/openg2p-lab/registration/household-change-evidence');PRIVATE.mkdir(mode=0o700,exist_ok=True)
phase=sys.argv[1];name=sys.argv[2] if len(sys.argv)>2 else None
def save(n,s):(OUT/(n+'.json')).write_text(json.dumps(s,indent=2,default=str))
def load(n):return json.loads((OUT/(n+'.json')).read_text())
def get(s):return call('aarin@gmail.com','change-request/get',{'change_request_id':s['cr']['id']})[0]
def value(s):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT rooms_count FROM g2p_register_households WHERE internal_record_id=%s',(s['internal_id'],));return q.fetchone()[0]
def check(n,s,label):
 if label not in s['checks']:s['checks'].append(label)
 save(n,s);print('PASS '+n+': '+label,flush=True)
def history_count(s):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT count(*) FROM g2p_register_history_households WHERE internal_record_id=%s',(s['internal_id'],));return q.fetchone()[0]
if phase=='prepare':
 password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];admin=login('https://g2p-odk.wverve.in','admin',password,True);r=admin.get('https://g2p-odk.wverve.in/v1/projects/1/app-users');r.raise_for_status();account=next(a for a in r.json() if a['displayName']=='Registry field capture · abuchi@gmail.com')
 for n in (sys.argv[2:] or ['returned','rejected','rejected-level2']):
  p=OUT/(n+'.json');s=load(n) if p.exists() else {'checks':[],'instance':'uuid:'+str(uuid.uuid4()),'record_name':'Meeting Verification Published Household '+n};s['internal_id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+s['instance']));save(n,s)
  if not s.get('uploaded'):
   d=E.parse('/opt/openg2p-lab/registration/household-final-e2e-private-evidence/physical-final.xml').getroot();d.find('meta/instanceID').text=s['instance'];d.find('household/record_name').text=s['record_name'];r=requests.post('https://g2p-odk.wverve.in/v1/key/'+account['token']+'/projects/1/submission',files={'xml_submission_file':('submission.xml',E.tostring(d),'text/xml')},headers={'X-OpenRosa-Version':'1.0'},verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=45);assert r.status_code in [201,202];s['uploaded']=True;save(n,s)
  for _ in range(40):
   with connect() as c:
    with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(s['internal_id'],));row=q.fetchone()
   if row:s['id']=str(row[0]);save(n,s);break
   time.sleep(2)
  assert s.get('id')
  if not master(s):
   if not any(t['stage_order']==2 for t in tasks(s)):decide(s,'abutu@gmail.com','approve','Publish isolated change-request test fixture.')
   wait_for(lambda:any(t['stage_order']==2 for t in tasks(s)),'Second fixture approval');decide(s,'adaku@gmail.com','approve','Independent fixture publication.',stage=2);wait_for(lambda:master(s),'Fixture publication')
  if not s.get('cr'):
   with connect() as c:
    with c.cursor() as q:q.execute("SELECT tab_id FROM g2p_register_ui_tab_sections WHERE section_id='hh_dwelling_services' LIMIT 1");s['tab_id']=q.fetchone()[0]
   body={'register_id':REG,'register_mnemonic':'Household','section_register_id':REG,'tab_id':s['tab_id'],'section_id':'hh_dwelling_services','internal_record_id':s['internal_id'],'edit_action':'UPDATE','section_records':[{'internal_record_id':s['internal_id'],'edit_action':'UPDATE','rooms_count':3}]};result,_=call('aarin@gmail.com','change-request/create',body);s['cr']={'id':result['change_request_id'],'body':body};s['cr']['request_id']=get(s)['awe_request_id'];s['baseline_history']=history_count(s);save(n,s)
  assert value(s)==2;check(n,s,'Isolated household published normally; proposed change leaves master unchanged')
else:
 s=load(name);d=get(s);s['cr']['request_id']=d['awe_request_id']
 if phase=='baseline':
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(s['internal_id'],));baseline=q.fetchone()[0]
  assert baseline['rooms_count']==2;p=PRIVATE/(name+'-baseline.json')
  if not p.exists():p.write_text(json.dumps(baseline));p.chmod(0o600)
  check(name,s,'Original household business-data baseline recorded before applying any change')
 elif phase=='returned':
  d=wait_for(lambda:get(s) if str(get(s).get('awe_request_status_summary')).startswith('returned') else None,'Returned change');s['return_count']=sum(e['event_type']=='request_returned' for e in d.get('review_history',[]));s['expected_proposal']=4 if s['return_count']==1 else 5;assert d['approval_status']=='PENDING' and value(s)==2;check(name,s,'Returned proposal and reasons retained; master remains unchanged')
 elif phase=='resubmitted':
  d=get(s);assert d['change_request_id']==s['cr']['id'] and d['approval_status']=='PENDING';assert not str(d['awe_request_status_summary']).startswith('returned');assert d['change_payload'][0]['rooms_count']==s['expected_proposal'];assert value(s)==2 and history_count(s)==s['baseline_history'];assert any(t['stage_order']==1 and t['status']=='open' for t in call('abutu@gmail.com','awe/tasks-for-request',{'request_id':d['awe_request_id']})[0]['tasks']);check(name,s,'Correction resubmits the same request, restarts level 1, and does not alter master/history')
 elif phase=='level1':
  wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in call('adaku@gmail.com','awe/tasks-for-request',{'request_id':d['awe_request_id']})[0]['tasks']),'Second change approval');assert value(s)==2 and history_count(s)==s['baseline_history'];check(name,s,'First approval activates level 2 without applying the proposal')
 elif phase=='approved':
  wait_for(lambda:value(s)==s['expected_proposal'],'Change applied');d=get(s);assert d['approval_status']=='APPROVED';s['review_history']=d.get('review_history',[]);assert sum(e['event_type']=='request_returned' for e in s['review_history'])==2;assert history_count(s)==s['baseline_history']+1
  before=json.loads((PRIVATE/(name+'-baseline.json')).read_text())
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(s['internal_id'],));after=q.fetchone()[0]
  ignored={'rooms_count','last_updated_at','last_updated_by','last_approved_at','last_approved_by','change_request_id'};changed=[k for k in before if k not in ignored and before[k]!=after.get(k)];assert not changed,'Unrelated fields changed: '+','.join(changed)
  s['status']='passed';check(name,s,'Both approvals apply only the corrected value and create one version-history entry; both returns preserved')
 elif phase=='history-approved':
  wait_for(lambda:value(s)==3,'History test change applied');d=get(s);assert d['approval_status']=='APPROVED';assert d['current_register_data'][0]['rooms_count']==2
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT rooms_count FROM g2p_register_history_households WHERE change_request_id=%s',(s['cr']['id'],));assert q.fetchone()[0]==3
  s['status']='passed';check(name,s,'New history snapshots retain room count, and approved change comparison correctly shows old 2 / new 3')
 elif phase=='rejected':
  wait_for(lambda:get(s)['approval_status']=='REJECTED','Permanent change rejection');assert value(s)==2 and history_count(s)==s['baseline_history'];d=get(s);s['review_history']=d.get('review_history',[]);assert any(e['event_type']=='request_rejected' for e in s['review_history']);body,status=call('aarin@gmail.com','change-request/approve',{'change_request_id':s['cr']['id']},expect=False);assert status>=400 or body.get('error');assert get(s)['approval_status']=='REJECTED' and value(s)==2;s['status']='passed';check(name,s,'Permanent rejection is final; old request cannot apply changes and master/history remain unchanged')
 else:raise ValueError(phase)
 save(name,s)
