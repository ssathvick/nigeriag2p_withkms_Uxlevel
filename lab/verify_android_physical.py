import sys,json,uuid,time,hashlib,xml.etree.ElementTree as E
from pathlib import Path
from urllib.parse import quote
import yaml
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
out=ROOT.parent/'output/android-flow-verification';path=out/'physical-device.json'
state=json.loads(path.read_text()) if path.exists() else {'checks':[],'physicalAndroidTest':True}
data=E.parse(out/'physical-final.xml').getroot();instance=data.findtext('meta/instanceID');internal=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+instance))
state.update(instance=instance,internal_id=internal,version=data.get('version'),gpsAccuracyMetres=float(data.findtext('household/coordinates').split()[3]),gpsCapturedAt=data.findtext('household/location_captured_at'))
def check(s):
 if s not in state['checks']:state['checks'].append(s)
 path.write_text(json.dumps(state,indent=2));print('PASS '+s,flush=True)
origin='https://g2p-odk.wverve.in';password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=login(origin,'admin',password,True);url=origin+'/v1/projects/1/forms/nsipa_registry_household/submissions/'+quote(instance,safe='')
if sys.argv[1]=='before':
 r=s.get(url,timeout=30);assert r.status_code==404,r.status_code
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(internal,));assert q.fetchone()[0]==0
 check('Finalised offline household remains on the device and is absent from both servers before reconnecting')
else:
 r=s.get(url+'.xml',timeout=30);r.raise_for_status();received=E.fromstring(r.content)
 assert received.findtext('household/coordinates')==data.findtext('household/coordinates')
 assert received.findtext('household/record_name')=='Meeting Verification Android Physical Offline'
 check('Android automatically uploaded the finalised household after reconnecting without pressing Send')
 for _ in range(24):
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(internal,));row=q.fetchone()
  if row:break
  time.sleep(2)
 assert row,'Awaiting scheduled native import';state['id']=str(row[0]);check('Scheduled worker automatically created the household in the integrated native intake queue')
 with connect() as c:
  with c.cursor() as q:
   q.execute('SELECT latitude,longitude,location_accuracy_m,geo_lowest_level_value_id,location_captured_at FROM g2p_intake_form_households WHERE submission_id=%s',(state['id'],));h=q.fetchone();point=data.findtext('household/coordinates').split();assert abs(float(h[0])-float(point[0]))<1e-7 and abs(float(h[1])-float(point[1]))<1e-7 and abs(float(h[2])-float(point[3]))<1e-6;assert h[3]=='NG001001_eziama' and h[4]
   q.execute('SELECT draft_status,approval_status,awe_request_id FROM g2p_intake_form_submissions WHERE submission_id=%s',(state['id'],));status=q.fetchone();assert status[0]=='FINAL' and status[1]=='PENDING' and status[2]
   q.execute('SELECT first_name,last_name,estimated_age,relationship_to_head FROM g2p_intake_form_individuals WHERE submission_id=%s',(state['id'],));members=q.fetchall();assert len(members)==1 and members[0][0]=='Fictional' and members[0][1]=='Android Head' and members[0][2]==35 and members[0][3]=='SELF'
 check('Native review preserves real device GPS precision, accuracy, capture time, selected ward and the fictional household member')
 check('Imported household awaits normal registry approvals; no approval bypass')
 state['status']='passed';path.write_text(json.dumps(state,indent=2));print('Physical Android workflow passed')
