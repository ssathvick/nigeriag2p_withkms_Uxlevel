"""Replay the real device-captured fictional interview through normal mobile ingestion and approvals."""
import sys,json,uuid,time,datetime,xml.etree.ElementTree as E
from pathlib import Path
import yaml,requests
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
from test_meeting_native_workflow import call,REG,FORM,decide,detail,wait_for,master,tasks
OUT=ROOT.parent/'output/mobile-approval-verification';OUT.mkdir(exist_ok=True);STATE=OUT/'workflow.json'
state=json.loads(STATE.read_text()) if STATE.exists() else {'instance':'uuid:'+str(uuid.uuid4()),'checks':[]}
def save():STATE.write_text(json.dumps(state,indent=2,default=str))
def check(label):
 if label not in state['checks']:state['checks'].append(label)
 save();print('PASS '+label,flush=True)
data=E.parse('/opt/openg2p-lab/registration/android-acceptance-private-evidence/physical-final.xml').getroot()
data.find('meta/instanceID').text=state['instance'];data.find('household/record_name').text='Meeting Verification Mobile Approval Lifecycle'
state['internal_id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+state['instance']));state['source']='Actual Android-captured interview replayed with a fresh test instance UUID; no new hardware capture claimed';save()
if not state.get('uploaded'):
 password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login('https://g2p-odk.wverve.in','admin',password,True);r=s.get('https://g2p-odk.wverve.in/v1/projects/1/app-users',timeout=30);r.raise_for_status();a=next(x for x in r.json() if x['displayName']=='Registry field capture · abuchi@gmail.com')
 r=requests.post('https://g2p-odk.wverve.in/v1/key/'+a['token']+'/projects/1/submission',files={'xml_submission_file':('submission.xml',E.tostring(data),'text/xml')},headers={'X-OpenRosa-Version':'1.0'},verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=45);assert r.status_code in [201,202],r.status_code;state['uploaded']=True;save()
 check('Real mobile interview payload accepted through authenticated field submission endpoint')
if not state.get('id'):
 for _ in range(60):
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(state['internal_id'],));row=q.fetchone()
  if row:state['id']=str(row[0]);save();break
  time.sleep(2)
 assert state.get('id'),'Awaiting scheduled mobile import'
check('Scheduled worker created the mobile household in native registration review')
if not state.get('returned'):
 assert detail(state)['approval_status']=='PENDING' and not master(state)
 bad,status=decide(state,'adaku@gmail.com','approve','Invalid L2 attempt at L1',expect=False);assert status>=400 or bad.get('error')
 check('Level 2 reviewer cannot perform the level 1 decision')
 decide(state,'abutu@gmail.com','return','Fictional mobile registration review: correct community description.')
 wait_for(lambda:detail(state)['draft_status']=='DRAFT','Return to registration officer')
 state['returned']=True;save();check('Registration review returns the same mobile intake for correction with recorded reason')
if not state.get('resubmitted'):
 call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':state['id'],'form_id':FORM,'register_id':REG,'section_id':'hh_survey_consent','section_register_id':REG,'section_payload':[{'internal_record_id':state['internal_id'],'edit_action':'UPDATE','survey_community':'Fictional mobile household reviewed and corrected'}]})
 call('aarin@gmail.com','intake-form/finalize-intake-form-submission',{'submission_id':state['id'],'register_id':REG,'form_id':FORM})
 state['resubmitted']=True;save();check('Registration officer corrects and resubmits the same mobile household')
if not state.get('l1'):
 decide(state,'abutu@gmail.com','approve','Mobile household: consent, enumeration, member and GPS reviewed.')
 wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(state)),'L2 task')
 assert not master(state);state['l1']=True;save();check('Level 1 approval activates level 2 and does not publish prematurely')
if not state.get('l2'):
 bad,status=decide(state,'abutu@gmail.com','approve','Invalid L1 attempt at L2',stage=2,expect=False);assert status>=400 or bad.get('error')
 check('Level 1 reviewer cannot perform level 2 approval')
 decide(state,'adaku@gmail.com','approve','Independent final review of fictional mobile household completed.',stage=2)
 wait_for(lambda:detail(state)['approval_status']=='APPROVED','Final approval')
 wait_for(lambda:master(state),'Master publication');state['l2']=True;save();check('Level 2 approval publishes the mobile household to the Master Registry')
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT functional_record_id,latitude,longitude,location_accuracy_m,location_captured_at,geo_lowest_level_value_id,survey_community FROM g2p_register_households WHERE internal_record_id=%s',(state['internal_id'],));h=q.fetchone();point=data.findtext('household/coordinates').split();assert h[0] and abs(float(h[1])-float(point[0]))<1e-7 and abs(float(h[2])-float(point[1]))<1e-7 and abs(float(h[3])-float(point[3]))<1e-6 and h[4] and h[5]=='NG001001_eziama' and h[6]=='Fictional mobile household reviewed and corrected';state['functional_id']=h[0]
  q.execute('SELECT internal_record_id,functional_record_id,first_name,last_name,estimated_age,relationship_to_head FROM g2p_register_individuals WHERE link_internal_record_id=%s',(state['internal_id'],));members=q.fetchall();assert len(members)==1 and members[0][1] and members[0][2:] == ('Fictional','Android Head',35,'SELF');state['member_id']=members[0][0]
check('Published household and linked member have functional IDs; GPS, ward and reviewed correction are preserved')
history=detail(state).get('review_history',[]);types=[e['event_type'] for e in history];assert 'request_returned' in types;state['review_history']=history
with connect('awe') as c:
 with c.cursor() as q:q.execute('SELECT count(*) FROM approval_decision d JOIN approval_request r ON r.id=d.request_id WHERE r.artifact_id=%s',(state['id'],));assert q.fetchone()[0]>=3
check('Return, resubmission and both independent decisions remain in approval history')
state['status']='passed';save();print('Mobile registration-to-publication approval test passed')
