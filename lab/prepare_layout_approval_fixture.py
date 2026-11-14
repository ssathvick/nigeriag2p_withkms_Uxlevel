"""Replay the real device-captured fictional interview through normal mobile ingestion and approvals."""
import sys,json,uuid,time,datetime,xml.etree.ElementTree as E
from pathlib import Path
import yaml,requests
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
from test_meeting_native_workflow import call,REG,FORM,decide,detail,wait_for,master,tasks
OUT=ROOT.parent/'output/registry-layout-approval-fixture';OUT.mkdir(exist_ok=True);STATE=OUT/'workflow.json'
state=json.loads(STATE.read_text()) if STATE.exists() else {'instance':'uuid:'+str(uuid.uuid4()),'checks':[]}
def save():STATE.write_text(json.dumps(state,indent=2,default=str))
def check(label):
 if label not in state['checks']:state['checks'].append(label)
 save();print('PASS '+label,flush=True)
data=E.parse('/opt/openg2p-lab/registration/android-acceptance-private-evidence/physical-final.xml').getroot()
data.find('meta/instanceID').text=state['instance'];data.find('household/record_name').text='Meeting Verification Readability Approval Record With A Long Household Name'
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
