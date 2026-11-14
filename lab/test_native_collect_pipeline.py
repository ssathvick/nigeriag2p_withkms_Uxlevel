import copy,json,time,uuid,xml.etree.ElementTree as E,yaml,requests
from pathlib import Path
import test_meeting_native_workflow as t
from test_mbr_db_connection import connect
from test_location_import_e2e import login
OUT=t.OUT;path=OUT/'native-collect-state.json';state=json.loads(path.read_text()) if path.exists() else {'instance':'uuid:'+str(uuid.uuid4())}
def save():path.write_text(json.dumps(state,indent=2))
root=Path(__file__).parent;fid='nsipa_registry_household';origin='https://g2p-odk.wverve.in'
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];admin=login(origin,'admin',password,True)
response=admin.get(origin+'/v1/projects/1/app-users',timeout=30);response.raise_for_status();account=next(a for a in response.json() if a['displayName']=='Registry field capture · abuchi@gmail.com')
server=origin+'/v1/key/'+account['token']+'/projects/1';ca='/opt/openg2p-lab/registration/ca-bundle.crt'
response=requests.get(server+'/formList',headers={'X-OpenRosa-Version':'1.0'},verify=ca,timeout=30);assert response.ok and fid in response.text,('Assigned full native form must be downloadable',response.status_code,response.text[:120])
t.check('Field QR grants the full native household form')
if not state.get('uploaded'):
 source=E.parse(root/'meeting-native'/ (fid+'.xml'));data=next(e for e in source.getroot().iter() if e.tag=='data');data=copy.deepcopy(data)
 for e in data.iter():e.attrib.pop('{http://openrosa.org/javarosa}template',None)
 values={'visit/sponsor_name':'NSIPA','visit/respondent_name':'Fictional Offline Head','visit/enumerator_name':'abuchi@gmail.com','visit/consent_status':'YES','visit/survey_community':'Fictional offline verification','household/record_name':'Meeting Verification Offline Full Household','household/address_line_1':'Fictional test address','household/coordinates':'9.92 8.89 1250 4','members/first_name':'Fictional','members/last_name':'Offline Head','members/gender':'MALE','members/estimated_age':'34','members/relationship_to_head':'SELF','living/rooms_count':'2','living/monthly_household_income':'12000','living/income_source':'AGRICULTURE','living/health_insurance_status':'NO','assets/asset_type':'PRODUCTIVE_TOOL','assets/asset_category':'Fictional farm tool','assets/quantity':'1','review/confirmation':'YES','meta/instanceID':state['instance']}
 for p,v in values.items():data.find(p).text=v
 second=copy.deepcopy(data.find('members'))
 for child in second:child.text=None
 for k,v in {'first_name':'Fictional','last_name':'Offline Child','gender':'FEMALE','birth_date':'2015-02-01','relationship_to_head':'CHILD'}.items():second.find(k).text=v
 data.insert(list(data).index(data.find('members'))+1,second)
 xml=E.tostring(data,encoding='utf-8',xml_declaration=True)
 response=requests.post(server+'/submission',files={'xml_submission_file':('submission.xml',xml,'text/xml')},headers={'X-OpenRosa-Version':'1.0'},verify=ca,timeout=45)
 assert response.status_code in [201,202],('OpenRosa submission',response.status_code)
 state['uploaded']=True;save();t.check('Authenticated field client uploads through Collect submission endpoint')
internal=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+state['instance']));state['internal_id']=internal;save()
def imported():
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(internal,));r=q.fetchone();return str(r[0]) if r else None
for _ in range(80):
 sid=imported()
 if sid:break
 time.sleep(1)
assert sid,'Scheduled native offline import did not create an intake';state['id']=sid;save()
def pending():
 d=t.call('aarin@gmail.com','intake-form/get-intake-form-submission',{'submission_id':sid,'register_id':t.REG})[0]
 return d if d.get('awe_request_id') else None
detail=t.wait_for(pending,'Full offline native approval request')
t.check('Full offline form automatically reaches native review queue',detail['approval_status']=='PENDING' and detail['draft_status']=='FINAL')
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT count(*),count(birth_date),count(estimated_age) FROM g2p_intake_form_individuals WHERE submission_id=%s',(sid,));assert q.fetchone()==(2,1,1)
  q.execute('SELECT count(*) FROM g2p_intake_form_household_assets WHERE submission_id=%s',(sid,));assert q.fetchone()[0]==1
  q.execute('SELECT consent_status,enumerator_name,monthly_household_income,health_insurance_status FROM g2p_intake_form_households WHERE submission_id=%s',(sid,));row=q.fetchone();assert row==('YES','abuchi@gmail.com',12000,'NO')
t.check('Offline roster supports age or date of birth and preserves repeat members')
t.check('Offline assets, consent, maker and optional welfare fields are preserved')
state['status']='passed';save();print('Full offline native pipeline passed; physical disconnected-device test remains unverified.')
