import copy,json,time,uuid,xml.etree.ElementTree as E,sys,hashlib,requests,yaml,datetime
from pathlib import Path
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
OUT=ROOT.parent/'output/android-flow-verification';OUT.mkdir(parents=True,exist_ok=True);path=OUT/'server-pipeline.json';state=json.loads(path.read_text()) if path.exists() else {'instance':'uuid:'+str(uuid.uuid4()),'checks':[]}
def save():path.write_text(json.dumps(state,indent=2,default=str))
def check(label):
 if label not in state['checks']:state['checks'].append(label)
 save();print('PASS',label,flush=True)
namespace={'__file__':str(ROOT/'test_parity_collect_mapping.py')};source=(ROOT/'test_parity_collect_mapping.py').read_text();exec(source[:source.index("setv('geography/lga_id'")],namespace)
data=namespace['data'];data.find('meta/instanceID').text=state['instance'];data.find('household/record_name').text='Meeting Verification Android Server Pipeline';data.find('household/location_captured_at').text=datetime.datetime.now(datetime.timezone.utc).isoformat();xml=E.tostring(data,encoding='utf-8',xml_declaration=True)
origin='https://g2p-odk.wverve.in';fid='nsipa_registry_household';password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];admin=login(origin,'admin',password,True);r=admin.get(origin+'/v1/projects/1/app-users',timeout=30);r.raise_for_status();account=next(a for a in r.json() if a['displayName']=='Registry field capture · abuchi@gmail.com');server=origin+'/v1/key/'+account['token']+'/projects/1';ca='/opt/openg2p-lab/registration/ca-bundle.crt'
r=requests.get(server+'/formList',headers={'X-OpenRosa-Version':'1.0'},verify=ca,timeout=30);r.raise_for_status();assert fid in r.text;check('Scoped field client can discover the current household form')
r=admin.get(origin+'/v1/projects/1/forms/'+fid+'.xml',timeout=30);r.raise_for_status();assert r.content==(ROOT/'household-parity/nsipa_registry_household.xml').read_bytes();check('Published mobile form matches the reviewed 2026111302 definition')
if not state.get('uploaded'):
 r=requests.post(server+'/submission',files={'xml_submission_file':('submission.xml',xml,'text/xml')},headers={'X-OpenRosa-Version':'1.0'},verify=ca,timeout=45);assert r.status_code in [201,202],r.status_code;state['uploaded']=True;save();check('Authenticated OpenRosa submission accepted with dummy household and GPS metadata')
internal=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+state['instance']));state['internal_id']=internal;save()
for _ in range(90):
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(internal,));row=q.fetchone()
 if row:break
 time.sleep(1)
assert row,'Automatic import did not create native intake';state['id']=str(row[0]);save();check('Scheduled sync worker imports the field submission automatically')
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT latitude,longitude,location_accuracy_m,geo_lowest_level_value_id,shock_types,crops_grown,television_count FROM g2p_intake_form_households WHERE submission_id=%s',(state['id'],));h=q.fetchone();assert float(h[0])==9.0765 and float(h[1])==7.3986 and float(h[2])==12 and h[3]=='NG001001_eziama' and h[4]==['Flood','Fire'] and h[5]==['Maize','Cassava'] and h[6]==2
  q.execute('SELECT draft_status,approval_status,awe_request_id FROM g2p_intake_form_submissions WHERE submission_id=%s',(state['id'],));status=q.fetchone();assert status[0]=='FINAL' and status[1]=='PENDING' and status[2]
  q.execute('SELECT count(*) FROM g2p_intake_form_individuals WHERE submission_id=%s',(state['id'],));assert q.fetchone()[0]==1
check('Native review queue preserves GPS precision, Nigeria ward, crops, shock choices, assets and member')
# Re-delivery must not create another native household.
r=requests.post(server+'/submission',files={'xml_submission_file':('submission.xml',xml,'text/xml')},headers={'X-OpenRosa-Version':'1.0'},verify=ca,timeout=45);assert r.status_code in [201,202,409],r.status_code
with connect() as c:
 with c.cursor() as q:q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(internal,));assert q.fetchone()[0]==1
check('Submission retry does not duplicate the native household')
state.update(status='passed',physicalAndroidTest=False);save();print('Server pipeline passed; Android GPS and disconnected capture still require the connected device.')
