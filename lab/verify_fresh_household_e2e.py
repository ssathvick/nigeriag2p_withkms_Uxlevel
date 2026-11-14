import sys,json,uuid,time,xml.etree.ElementTree as E
from pathlib import Path
from urllib.parse import quote
import yaml
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
from test_meeting_native_workflow import detail,tasks,master,wait_for
OUT=ROOT.parent/'output/household-final-e2e';path=OUT/'workflow.json';state=json.loads(path.read_text()) if path.exists() else {'checks':[],'physicalAndroidTest':True}
data=E.parse(OUT/'physical-final.xml').getroot();instance=data.findtext('meta/instanceID');state.update(instance=instance,internal_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+instance)),record_name=data.findtext('household/record_name'),version=data.get('version'))
def save():path.write_text(json.dumps(state,indent=2,default=str))
def check(label):
 if label not in state['checks']:state['checks'].append(label)
 save();print('PASS '+label,flush=True)
save();phase=sys.argv[1]
if phase in ['before','after']:
 password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login('https://g2p-odk.wverve.in','admin',password,True);url='https://g2p-odk.wverve.in/v1/projects/1/forms/nsipa_registry_household/submissions/'+quote(instance,safe='')
 if phase=='before':
  r=s.get(url,timeout=30);assert r.status_code==404,r.status_code
  check('Fresh interview captured, reopened and finalised on Android while offline; no server submission before reconnect')
 else:
  r=s.get(url+'.xml',timeout=30);assert r.status_code==200,r.status_code
  received=E.fromstring(r.content);assert received.findtext('household/coordinates')==data.findtext('household/coordinates')
  check('Android automatically sent the fresh interview after reconnecting without pressing Send')
  for _ in range(40):
   with connect() as c:
    with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(state['internal_id'],));row=q.fetchone()
   if row:state['id']=str(row[0]);save();break
   time.sleep(2)
  assert state.get('id'),'Waiting for scheduled import';assert detail(state)['approval_status']=='PENDING' and not master(state)
  check('Scheduled worker imported the household into native registration review with normal pending approvals')
elif phase=='level1':
 wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(state)),'Second approval activated');assert not master(state)
 check('First approval completed through the UI; second review activated without early publication')
elif phase=='level2':
 wait_for(lambda:detail(state)['approval_status']=='APPROVED','Second approval');wait_for(lambda:master(state),'Master publication')
 check('Second independent UI approval published the household to the Master Registry')
if phase in ['after','level2']:
 prefix='g2p_register_' if phase=='level2' else 'g2p_intake_form_'
 with connect() as c:
  with c.cursor() as q:
   q.execute('SELECT row_to_json(h) FROM '+prefix+'households h WHERE internal_record_id=%s',(state['internal_id'],));h=q.fetchone()[0];point=data.findtext('household/coordinates').split()
   assert h['record_name']==state['record_name'] and abs(float(h['latitude'])-float(point[0]))<1e-7 and abs(float(h['longitude'])-float(point[1]))<1e-7 and abs(float(h['location_accuracy_m'])-float(point[3]))<1e-6 and h['location_captured_at'] and h['geo_lowest_level_value_id']=='NG001001_eziama'
   assert h['sponsor_name']=='NG CARES' and h['income_source']=='Fishing' and float(h['monthly_household_income'])==1000 and h['rooms_count']==2 and set(h['shock_types'])=={'Flood','Fire'} and h['health_insurance_status']=='YES' and h['television_count']==2 and set(h['crops_grown'])=={'Cassava','Maize'}
   choices=json.loads((ROOT/'household-parity/odk_survey_choices.json').read_text())['choices'];assert h['roof_material']==choices['/data/living/roof_material'][data.findtext('living/roof_material')]
   q.execute('SELECT row_to_json(i) FROM '+prefix+'individuals i WHERE link_internal_record_id=%s',(state['internal_id'],));members=[r[0] for r in q.fetchall()];assert len(members)==1;member=members[0];assert member['first_name']=='Fictional' and member['last_name']=='Final Head' and member['estimated_age']==35 and member['relationship_to_head']=='SELF';assert h['household_head_internal_record_id']==member['internal_record_id'];state['member_id']=member['internal_record_id']
   if phase=='level2':assert h['functional_record_id'] and member['functional_record_id'];state['functional_id']=h['functional_record_id']
 check(('Published master' if phase=='level2' else 'Imported intake')+' preserves the member, head link, GPS, ward and all eight survey sections')
 if phase=='level2':
  state['review_history']=detail(state).get('review_history',[])
  with connect('awe') as c:
   with c.cursor() as q:q.execute('SELECT count(*) FROM approval_decision d JOIN approval_request r ON r.id=d.request_id WHERE r.artifact_id=%s',(state['id'],));assert q.fetchone()[0]==2
  check('Both independent approval decisions and the review history are retained')
  state['status']='passed';save()
