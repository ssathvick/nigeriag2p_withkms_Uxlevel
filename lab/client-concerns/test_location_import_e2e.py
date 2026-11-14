"""Live fictional ODK import, scheduled sync, independent approvals, read-only checks."""
import sys,json,uuid,hashlib,datetime,time,sqlite3,xml.etree.ElementTree as ET
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,quote,urlparse
import requests,yaml
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
ROOT=Path('/opt/openg2p-lab/odk-sync')
WORK=Path(__file__).parent/'location-e2e-verification';WORK.mkdir(exist_ok=True)
STATE=WORK/'state.json';REG='a0000000-0000-4000-8000-000000000002'
HOST='https://register.nigeriag2p.com';ODK='https://g2p-odk.wverve.in'
class Form(HTMLParser):
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='form' and a.get('id')=='kc-form-login':self.action=a['action']
def login(origin,user,password,odk=False):
 s=requests.Session();s.verify='/opt/openg2p-lab/registration/ca-bundle.crt'
 response=s.get(origin+('/v1/oidc/login' if odk else '/api/login?redirect_uri='+quote(origin+'/en',safe='')),timeout=30);response.raise_for_status()
 form=Form();form.feed(response.text)
 if not hasattr(form,'action'):raise RuntimeError('Expected sign-in form missing')
 response=s.post(urljoin(response.url,form.action),data={'username':user,'password':password,'credentialId':''},timeout=30);response.raise_for_status()
 if 'kc-form-login' in response.text:raise RuntimeError('Sign-in did not complete')
 if not odk and not any(c.name=='X-Access-Token' for c in s.cookies):
  print('Auth diagnostic:',[(x.status_code,urlparse(x.url).hostname,urlparse(x.url).path,[c.name for c in x.cookies]) for x in [*response.history,response]],flush=True)
  import re
  from http.cookies import SimpleCookie
  for hop in response.history:
   for raw in hop.raw.headers.getlist('Set-Cookie'):
    cookie=SimpleCookie();cookie.load(raw)
    print('Cookie scope diagnostic:',[(key,value['domain'],value['path']) for key,value in cookie.items()],flush=True)
  from urllib.parse import parse_qs
  print('Final query fields:',list(parse_qs(urlparse(response.url).query)),flush=True)
 s.headers['X-Requested-With']='XMLHttpRequest';return s
def post(s,path,data):
  # Match the normal browser's CSRF cookie/header contract.
 csrf=next((c.value for c in s.cookies if c.name=='X-CSRF-Token'),None)
 if csrf:s.headers['X-CSRF-Token']=csrf
 response=s.post(HOST+'/api/'+path,json=data,timeout=45)
 if not response.ok:raise RuntimeError(path+' HTTP '+str(response.status_code))
 return response.json()
def save(state):STATE.write_text(json.dumps(state,indent=2,default=str))
def status(state):
 with sqlite3.connect('file:'+str(ROOT/'ledger.sqlite')+'?mode=ro',uri=True) as c:
  c.row_factory=sqlite3.Row;entry=c.execute('SELECT * FROM imports WHERE instance_id=?',(state['instance'],)).fetchone()
  if not entry:return {'ledger_state':None}
  entry=dict(entry)
 with r.pg('register') as c:
  c.set_session(readonly=True)
  with c.cursor() as q:
   q.execute('SELECT row_to_json(h) FROM g2p_intake_form_households h WHERE internal_record_id=%s',(entry['internal_id'],));intakes=[x[0] for x in q.fetchall()]
   q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(entry['internal_id'],));records=[x[0] for x in q.fetchall()]
   q.execute('SELECT approval_status,register_ingest_process_status,awe_request_id FROM g2p_intake_form_submissions WHERE submission_id=%s',(entry['submission_id'],));submission=q.fetchone()
 return {'ledger_state':entry['state'],'ledger_error':entry['error'],'submission_id':entry['submission_id'],'internal_id':entry['internal_id'],'intakes':intakes,'records':records,'approval':submission[0] if submission else None,'ingest':submission[1] if submission else None,'request_id':submission[2] if submission else None}
def check_geo(row):
 assert row['geo_lowest_level_value_id']=='OCHA-NG032005',row.get('geo_lowest_level_value_id')
 hierarchy=row['geo_code_hierarchy_json']['hierarchy']
 assert [(v['level_value_id'],v['level_value_mnemonic']) for v in hierarchy]==[('NG','Nigeria'),('NG31','Plateau'),('OCHA-NG032005','Jos North')],hierarchy
def run():
 state=json.loads(STATE.read_text()) if STATE.exists() else {'instance':'uuid:'+str(uuid.uuid4()),'form':'nsipa_field_household_demo'}
 save(state)
 if not state.get('uploaded'):
  password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
  s=login(ODK,'admin',password,True)
  endpoint=ODK+'/v1/projects/1/forms/'+state['form']
  response=s.get(endpoint+'.xml',timeout=30);response.raise_for_status();definition=response.content
  cfg=json.loads((ROOT/'config.json').read_text());assert hashlib.sha256(definition).hexdigest()==cfg['definition_sha256'][state['form']]
  template=ET.fromstring((Path(__file__).parent/'odk-verification/0-numeric-source.xml').read_bytes())
  template.set('id',state['form']);template.set('version','2026111001')
  name='Synthetic Location Regression '+state['instance'][-8:]
  updates={'visit/enumerator_id':'NSIPA-LOCATION-E2E','visit/visit_date':datetime.date.today().isoformat(),'household/household_name':name+' Household','household/household_head_name':name,'household/sample_reference':'GEO-E2E-'+state['instance'][-8:],'meta/instanceID':state['instance'],'meta/instanceName':name+' - fictional location test'}
  for path,value in updates.items():template.find(path).text=value
  for tag in ['roof_material','water_source_type']:template.find('household').remove(template.find('household/'+tag))
  xml=ET.tostring(template,encoding='utf-8',xml_declaration=True)
  (WORK/'submitted.xml').write_bytes(xml);(WORK/'definition.xml').write_bytes(definition)
  response=s.post(endpoint+'/submissions',data=xml,headers={'Content-Type':'application/xml'},timeout=30)
  assert response.status_code in (200,201,409),'ODK upload HTTP '+str(response.status_code)
  response=s.get(endpoint+'/submissions/'+quote(state['instance'],safe='')+'.xml',timeout=30);response.raise_for_status()
  (WORK/'source.xml').write_bytes(response.content)
  state.update(uploaded=True,name=name+' Household',source_sha256=hashlib.sha256(response.content).hexdigest());save(state);s.close()
  print('ODK submission uploaded and read back:',state['instance'],flush=True)
 phase=sys.argv[1] if len(sys.argv)>1 else 'status'
 current=status(state)
 if current['ledger_state']!='SUBMITTED':print(json.dumps({'waiting_for_timer':True,'state':current},default=str));return
 if not state.get('before_approval'):
  assert len(current['intakes'])==1 and len(current['records'])==0
  check_geo(current['intakes'][0]);state['before_approval']=current;save(state)
  print('PASS pre-approval intake has Plateau/Jos North; registry record absent',flush=True)
 if phase in ('approve-one','approve-two'):
  number=1 if phase=='approve-one' else 2;key='after_review_'+str(number)
  if key not in state:
   if number==2:assert 'after_review_1' in state
   user='nsipa-demo-reviewer-'+('one' if number==1 else 'two')
   accounts=json.loads(Path('/opt/openg2p-lab/registration/client-demo-accounts.json').read_text())
   s=login(HOST,user,accounts[user]['password'])
   tasks=post(s,'awe/tasks-for-request',{'request_id':current['request_id']})
   opened=[t for t in tasks['tasks'] if t['status']=='open' and t['stage_order']==number]
   assert len(opened)==1,'Expected single reviewer task'
   task=opened[0]
   post(s,'awe/submit-task-decision',{'task_id':task['id'],'action':'approve','comment':'Fictional location regression: source and master-data hierarchy verified; Plateau and Jos North intact.','artifact_id':current['submission_id'],'artifact_type':'registry.intake_form','current_stage':number})
   s.close();state[key]={'decision_submitted':True,'reviewer':user};save(state)
   time.sleep(2);current=status(state)
   check_geo(current['intakes'][0])
   if number==1:assert len(current['records'])==0
   state[key]['observed']=current;save(state);print('PASS reviewer stage',number,flush=True)
 if current.get('ingest')=='PROCESSED':
  assert current['approval']=='APPROVED' and len(current['records'])==1 and len(current['intakes'])==1
  row=current['records'][0];check_geo(row)
  assert row['record_name']==state['name']
  assert row['latitude']==9.896527 and row['longitude']==8.858331
  with r.pg('awe') as c:
   with c.cursor() as q:
    q.execute('SELECT stage_order,actor,action FROM approval_decision WHERE request_id=%s ORDER BY stage_order',(current['request_id'],));decisions=q.fetchall()
  assert len(decisions)==2 and len({d[1] for d in decisions})==2 and all(d[2]=='approve' for d in decisions)
  state.update(finished=True,final=current,decisions=decisions);save(state)
  print(json.dumps({'PASS':True,'functional_id':row['functional_record_id'],'internal_id':row['internal_record_id'],'approval':current['approval'],'ingest':current['ingest'],'geography':row['geo_code_hierarchy_json'],'reviewer_stages':len(decisions)},indent=2))
 else:print(json.dumps({'approval':current.get('approval'),'ingest':current.get('ingest'),'registry_count':len(current.get('records',[]))}))
if __name__=='__main__':run()
