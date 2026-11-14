"""Scheduled ODK -> intake sync. Never approves; SQLite ledger and flock serialize creates."""
import os,sys,json,sqlite3,fcntl,hashlib,secrets,uuid,subprocess,datetime,logging
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import quote
import requests
from odk_household_mapping import map_submission
from odk_native_registry_mapping import map_native
from odk_legacy_mapping import map_legacy
from odk_geography import load_geography
ROOT=Path(os.environ.get('NSIPA_ODK_SYNC_HOME','/opt/openg2p-lab/odk-sync'))
REG='a0000000-0000-4000-8000-000000000002';FORM='c1000000-0000-4000-8000-000000000002'
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def service(name):return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
class LoginForm(HTMLParser):
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='form' and 'action' in a:self.action=a['action']
def db():
 c=sqlite3.connect(ROOT/'ledger.sqlite');c.row_factory=sqlite3.Row
 c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA synchronous=FULL')
 c.execute('CREATE TABLE IF NOT EXISTS imports(source_key TEXT PRIMARY KEY, form_id TEXT NOT NULL,instance_id TEXT NOT NULL,source_hash TEXT,internal_id TEXT,submission_id TEXT,state TEXT NOT NULL,error TEXT,updated_at TEXT NOT NULL)');c.commit();return c
def put(c,key,**fields):
 fields['updated_at']=now();c.execute('UPDATE imports SET '+','.join(k+'=?' for k in fields)+' WHERE source_key=?',(*fields.values(),key));c.commit()
def native_row(internal_id):
 # Read-only reconciliation after a lost HTTP response. No registry table writes.
 sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app
 with registration_app.pg('register') as c:
  with c.cursor() as q:
   q.execute('SELECT row_to_json(h),row_to_json(s) FROM g2p_intake_form_households h JOIN g2p_intake_form_submissions s ON h.submission_id=s.submission_id WHERE h.internal_record_id=%s',(internal_id,));rows=q.fetchall()
 if len(rows)>1:raise ValueError('Multiple native intakes found; manual reconciliation required')
 return rows[0] if rows else None
class Client:
 def __init__(self,cfg):
  self.cfg=cfg;self.odk=requests.Session();self.odk.verify='/opt/openg2p-lab/registration/ca-bundle.crt';self.origin=cfg['odk_origin']
  r=self.odk.get(self.origin+'/v1/oidc/login',timeout=30);r.raise_for_status();form=LoginForm();form.feed(r.text)
  if not hasattr(form,'action'):raise RuntimeError('ODK reader sign-in form unavailable')
  r=self.odk.post(form.action,data={'username':cfg['odk_username'],'password':cfg['odk_password'],'credentialId':''},timeout=30);r.raise_for_status()
  self.odk.headers['X-Requested-With']='XMLHttpRequest'
  self.api=requests.Session();csrf=secrets.token_urlsafe(32);self.api.headers['X-CSRF-Token']=csrf;self.api.cookies.set('X-CSRF-Token',csrf)
  r=requests.post(service('commons-keycloak')+'/realms/staff/protocol/openid-connect/token',data={'grant_type':'client_credentials','client_id':cfg['client_id'],'client_secret':cfg['client_secret']},timeout=30);r.raise_for_status();self.api.headers['Authorization']='Bearer '+r.json()['access_token']
  self.registry=service('register-staff-portal-api');self.master=service('commons-services-master-data-api')
 def get(self,path):
  r=self.odk.get(self.origin+path,timeout=30);r.raise_for_status();return r
 def post(self,path,payload,base=None):
  data={'request_header':{'sender_app_mnemonic':'NSIPA_ODK_SYNC','sender_app_url':self.origin,'request_id':str(uuid.uuid4()),'request_timestamp':now()},'request_body':{'request_payload':payload,'pagination_request':{'page_size':500,'current_page':1}}}
  r=self.api.post((base or self.registry)+path,json=data,timeout=45);r.raise_for_status();body=r.json()
  if body.get('response_header',{}).get('response_status')!='SUCCESS':raise ValueError('Native API rejected request: '+str(body.get('response_header',{}).get('response_error_code')))
  return body['response_body']['response_payload']
 def close(self):
  try:self.odk.delete(self.origin+'/v1/sessions/current',timeout=10)
  except requests.RequestException:pass
  self.odk.close();self.api.close()
def process(client,c,formid,definition,master,entry):
 instance=entry['instanceId'];key=f"central-main:1:{formid}:{instance}"
 c.execute('INSERT OR IGNORE INTO imports(source_key,form_id,instance_id,state,updated_at) VALUES(?,?,?,?,?)',(key,formid,instance,'DISCOVERED',now()));c.commit()
 row=dict(c.execute('SELECT * FROM imports WHERE source_key=?',(key,)).fetchone())
 xml=client.get(f'/v1/projects/1/forms/{quote(formid,safe="")}/submissions/{quote(instance,safe="")}.xml').content
 digest=hashlib.sha256(xml).hexdigest()
 if row['source_hash'] and row['source_hash']!=digest:
  put(c,key,state='SOURCE_CHANGED',error='Source changed; manual review required. Existing intake not overwritten.');return
 if row['state'] in ('SUBMITTED','EXISTING','QUARANTINED','SOURCE_CHANGED','EXCLUDED_TEST'):return
 try:
  review=getattr(client,'cfg',{}).get('legacy_reviews',{}).get(instance)
  if formid=='nsipa_registry_household':mapped=map_native(xml,definition,master)
  elif review:
   definition=(ROOT/'legacy-review'/review['definition_file']).read_bytes()
   mapped=map_legacy(xml,definition,master,review)
  else:mapped=map_submission(xml,definition,master)
 except (ValueError,KeyError,TypeError) as e:
  put(c,key,source_hash=digest,state='QUARANTINED',error=str(e)[:180]);logging.warning('Quarantined %s',key);return
 internal=mapped['payload']['internal_record_id'];put(c,key,source_hash=digest,internal_id=internal)
 evidence=ROOT/'receipts'/internal;evidence.mkdir(parents=True,exist_ok=True)
 for name,content in [('source.xml',xml),('definition.xml',definition),('mapping.json',json.dumps(mapped).encode())]:
  p=evidence/name
  if not p.exists():p.write_bytes(content)
 sid=row['submission_id']
 if not sid:
  found=native_row(internal)
  if found:
   saved,submission=found
   if any(saved.get(k)!=v for k,v in mapped['payload'].items()):
    put(c,key,state='QUARANTINED',error='Existing deterministic ID has different data; manual review required');return
   sid=submission['submission_id'];put(c,key,submission_id=sid,state='CREATED')
  elif row['state']=='CREATE_UNCERTAIN':
   # Never blind-retry a possibly committed create. A later pass may reconcile it.
   return
  else:
   put(c,key,state='CREATE_UNCERTAIN',error='Create reserved; reconcile before retry if response is lost')
   result=client.post('/intake-form-data/save_intake_form_submission',{'submission_id':None,'section_id':'hh_composition_headship','section_register_id':REG,'register_id':REG,'form_id':FORM,'section_payload':[{**mapped['payload'],'edit_action':'ADD','link_internal_record_id':''}]})
   sid=result['submission_id'];put(c,key,submission_id=sid,state='CREATED',error=None)
 current=client.post('/intake-form-data/get_intake_form_submission',{'submission_id':sid,'register_id':REG})
 if current.get('awe_request_id'):
  # Includes rejected/returned items: never automatically resubmit review decisions.
  put(c,key,state='SUBMITTED',error=None);return
 for section in mapped.get('section_payloads',[]):
  client.post('/intake-form-data/save_intake_form_submission',{'submission_id':sid,'register_id':REG,'form_id':FORM,**section})
 client.post('/intake-form-data/finalize_intake_form_submission',{'submission_id':sid,'register_id':REG,'form_id':FORM})
 put(c,key,state='SUBMITTED',error=None);logging.info('Submitted %s for independent review',key)
def run():
 os.umask(0o077);ROOT.mkdir(mode=0o700,exist_ok=True)
 with open(ROOT/'worker.lock','a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:logging.info('Another worker holds the lock; skipping');return
  cfg=json.loads((ROOT/'config.json').read_text());c=db();client=Client(cfg)
  try:
   master={'GEO_VALUES':load_geography()}
   for attr in ['ROOF_MATERIAL','WATER_SOURCE_TYPE']:
    value=client.post('/attributes/get_attribute_values',{'attribute_id':attr},client.master)
    master[attr]=value if isinstance(value,list) else value.get('attribute_values',value.get('values'))
    if not isinstance(master[attr],list):raise ValueError('Unexpected master-data response')
   failures=0
   for formid in cfg['forms']:
    prefix=f'/v1/projects/1/forms/{formid}'
    definition=client.get(prefix+'.xml').content
    expected=cfg.get('definition_sha256',{}).get(formid)
    if not expected or hashlib.sha256(definition).hexdigest()!=expected:
     failures+=1;logging.error('Published definition changed for %s; mapping review required',formid);continue
    # Central submissions listing is unpaginated (all current submissions).
    entries=client.get(prefix+'/submissions').json()
    for entry in entries:
     try:process(client,c,formid,definition,master,entry)
     except Exception as e:
      failures+=1;logging.error('Submission processing failed (%s); retry/reconcile on next pass',type(e).__name__)
   counts=dict(c.execute('SELECT state,count(*) FROM imports GROUP BY state').fetchall())
   status={'last_completed_at':now(),'counts':counts,'transient_failures':failures};(ROOT/'status.json.tmp').write_text(json.dumps(status,indent=2));os.replace(ROOT/'status.json.tmp',ROOT/'status.json')
   logging.info('Sync pass complete: %s',json.dumps(status))
   if failures:raise RuntimeError('Some submissions need retry; inspect ledger and journal')
  finally:client.close();c.close()
if __name__=='__main__':run()
