"""Jos synthetic cohort orchestration. Native services; local Example Bank only."""
import json,uuid,datetime,subprocess,base64,hashlib,logging
from pathlib import Path
import requests,yaml
from flask import Blueprint,g,request,redirect,abort
POLICY='jos.cct.synthetic.payment.v1'
MNEMONIC='IQS_INTEGRATED_JOS_CCT_DEMO'
TREASURY='JOS-DEMO-TREASURY'
BANK='openg2p-g2p-bridge-example-bank-api'
AMOUNT=25000
IDS=['JOS-NATIVE-001','JOS-NATIVE-002','JOS-NATIVE-003']
class GuardError(ValueError):pass
def ensure(ok,message):
 if not ok:raise GuardError(message)
def init(r):
 with r.db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS jos_runs(id TEXT PRIMARY KEY,sub TEXT UNIQUE,program_id INTEGER,cycle_id INTEGER,list_id INTEGER,awe_id TEXT,condition TEXT DEFAULT 'pending',dispatch_started INTEGER DEFAULT 0,statement_requested INTEGER DEFAULT 0,updated TEXT);
  CREATE TABLE IF NOT EXISTS jos_events(id INTEGER PRIMARY KEY,run_id TEXT,actor TEXT,action TEXT,at TEXT);''')
def run(r,key):
 ensure(key in IDS,'Unknown Jos sample.');x=r.one('SELECT * FROM jos_runs WHERE id=?',(key,));ensure(x,'Prepare the connected sample cohort first.');return x
def profile(r,x):
 p=r.one('SELECT * FROM profiles WHERE sub=?',(x['sub'],));ensure(p and p['sub']=='jos-native:'+x['id'],'Sample identity mismatch.')
 d=json.loads(p['data']);ensure(d.get('synthetic') is True and d.get('jos_demo')==x['id'] and d['household_name'].startswith('SAMPLE JOS'),'Only the fixed fictional Jos cohort is permitted.')
 return p
def event(r,key,actor,action):r.execute('INSERT INTO jos_events(run_id,actor,action,at) VALUES(?,?,?,?)',(key,actor,action,r.stamp()));r.execute('UPDATE jos_runs SET updated=? WHERE id=?',(r.stamp(),key))
def routing_guard(r):
 d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy','bridge-celery-worker','-o','json']))
 env={x['name']:x.get('value') for x in d['spec']['template']['spec']['containers'][0].get('env',[])}
 for prefix in ['G2P_BRIDGE_BANK_CONNECTORS_','G2P_BRIDGE_CELERY_WORKERS_']:
  for key,path in [('FUNDS_AVAILABLE_CHECK','check_funds'),('FUNDS_BLOCK','block_funds'),('FUNDS_DISBURSEMENT','initiate_payment')]:
   ensure(env.get(prefix+key+'_URL_EXAMPLE_BANK')=='http://'+BANK+'/'+path,'Local Example Bank route changed. Dispatch blocked.')
 ensure(env.get('G2P_BRIDGE_MAPPER_CONNECTORS_SPAR_MAPPER_URL')=='http://spar-openg2p-spar-mapper-api/mapper/resolve','Mapper route changed.')
 d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',BANK.replace('-api','-celery'),'-o','json']))
 env={x['name']:x.get('value') for x in d['spec']['template']['spec']['containers'][0].get('env',[])}
 ensure(env.get('EXAMPLE_BANK_CELERY_MT940_STATEMENT_CALLBACK_URL')=='http://bridge-api/upload_mt940','Statement callback is not the local Bridge.')
 for svc in [BANK,'bridge-api','spar-openg2p-spar-mapper-api']:
  s=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','svc',svc,'-o','json']))
  ensure(s['spec'].get('type','ClusterIP')=='ClusterIP' and not s['spec'].get('externalName') and not s['spec'].get('externalIPs'),'Simulator must remain a local ClusterIP service.')
 return True
def awe_client(r):
 password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];kc=r.svc('commons-keycloak')
 t=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);t.raise_for_status()
 ks=requests.Session();ks.headers['Authorization']='Bearer '+t.json()['access_token'];client=ks.get(kc+'/admin/realms/staff/clients',params={'clientId':'awe-admin-portal'},timeout=20);client.raise_for_status();cid=client.json()[0]['id']
 secret=ks.get(kc+'/admin/realms/staff/clients/'+cid+'/client-secret',timeout=20);secret.raise_for_status()
 t=requests.post(kc+'/realms/staff/protocol/openid-connect/token',data={'client_id':'awe-admin-portal','client_secret':secret.json().get('value',''),'grant_type':'password','username':'admin','password':password},timeout=20);t.raise_for_status()
 s=requests.Session();s.headers['Authorization']='Bearer '+t.json()['access_token'];return s,r.svc('commons-services-awe')+'/v1/awe'
def awe_post(s,url,payload=None):
 response=s.post(url,json=payload,timeout=25);response.raise_for_status();return response.json() if response.content else {}
def prepare(r):
 init(r)
 with r.LOCK:
  existing=r.one('SELECT * FROM programs WHERE mnemonic=?',(MNEMONIC,))
  pid=existing['id'] if existing else r.create_program(MNEMONIC,'SAMPLE Jos CCT — connected local-bank demo',AMOUNT,100000,2)
  pb=r.Odoo('pbms-odoo','pbmsdb')
  # Restrict this benefit rule to this exact three-household cohort, never all registry fixtures.
  refs=['IQS-REG-HH-'+uuid.uuid5(uuid.NAMESPACE_URL,'jos-native:'+key+'/household').hex[:16] for key in IDS]
  pb.upsert('g2p.entitlement.rule.definition',[['mnemonic','=',MNEMONIC+'-ENT']],{'mnemonic':MNEMONIC+'-ENT','program_id':pid,'target_registry':'household','benefit_code_id':r.one('SELECT benefit_id FROM programs WHERE id=?',(pid,))['benefit_id'],'quantity':AMOUNT,'pbms_domain':repr(['|','|']+[('link_registry_id','=',ref) for ref in refs])})
  for i,key in enumerate(IDS):
   sub='jos-native:'+key;members=[{'given':'SAMPLE','family':key+' ADULT','birth_date':'1990-01-01','gender':'Female','ref':'IQS-REG-I-'+uuid.uuid5(uuid.NAMESPACE_URL,sub+'/adult').hex[:16]},{'given':'SAMPLE','family':key+' CHILD','birth_date':'2015-01-01','gender':'Male','ref':'IQS-REG-I-'+uuid.uuid5(uuid.NAMESPACE_URL,sub+'/child').hex[:16]}]
   data={'synthetic':True,'jos_demo':key,'members':members,'state':'NG31','state_name':'Plateau','community':'SAMPLE Jos planning area — LGA mapping pending','household_name':'SAMPLE JOS CONNECTED HOUSEHOLD '+str(i+1),'monthly_income':30000,'email':key.lower()+'@example.invalid','geography':{'lga_id':None,'ward':None,'coordinate_source':'not_captured'}}
   r.execute("INSERT OR IGNORE INTO profiles(sub,ref,household_ref,data,status,updated) VALUES(?,?,?,?,'pending_review',?)",(sub,members[0]['ref'],refs[i],json.dumps(data),r.stamp()))
   r.execute('INSERT OR IGNORE INTO jos_runs(id,sub,program_id,updated) VALUES(?,?,?,?)',(key,sub,pid,r.stamp()));profile(r,run(r,key))
  with r.pg('awe') as c:
   with c.cursor() as cur:cur.execute('SELECT id FROM approval_policy WHERE policy_key=%s',(POLICY,));found=cur.fetchone()
  if not found:
   session,url=awe_client(r);awe_post(session,url+'/policies',{'policy_key':POLICY,'name':'SAMPLE Jos CCT local-bank release','description':'Synthetic cohort only. Native AWE approval gates local Example Bank dispatch. Not production separation of duties.','artifact_type':'jos.synthetic.payment','stages':[{'name':'Sandbox payment review','stage_order':1,'mode':'all','rules':[{'rule_type':'user','rule_value':{'user_id':'admin'}}]}]});awe_post(session,url+'/policies/'+POLICY+'/versions/1/activate')
 return pid
def approval(r,x):
 with r.pg('awe') as c:
  with c.cursor() as cur:
   cur.execute('SELECT id,status,context,policy_key FROM approval_request WHERE artifact_id=%s AND policy_key=%s ORDER BY created_at',(x['id']+'-C01',POLICY));items=cur.fetchall();ensure(len(items)<=1,'Duplicate approval requests; review required.')
   if not items:return None
   aid,status,context,policy=items[0];cur.execute("SELECT id,status,assignee FROM approval_task WHERE request_id=%s ORDER BY created_at",(aid,));tasks=cur.fetchall()
   return {'id':aid,'status':status,'context':context,'policy':policy,'tasks':[{'id':v[0],'status':v[1],'assignee':v[2]} for v in tasks]}
def calculation(r,x):
 if not x['list_id']:return None,[]
 pb=r.Odoo('pbms-odoo','pbmsdb');l=pb.call('g2p.beneficiary.list','read',[[x['list_id']]],{'fields':['beneficiary_list_id','eligibility_process_status','entitlement_process_status','number_of_registrants','number_of_entitlements_processed','list_workflow_status','envelope_creation_status','envelope_creation_latest_error_code']})[0]
 with r.pg('bgtaskdb','pbms-postgresql') as c:
  with c.cursor() as cur:
   cur.execute('SELECT registrant_details FROM beneficiary_list_details WHERE beneficiary_list_id=%s',(l['beneficiary_list_id'],));details=[d for chunk, in cur.fetchall() for d in chunk]
 return l,details
def assert_calculation(r,x):
 p=profile(r,x);program=r.one('SELECT * FROM programs WHERE id=?',(x['program_id'],));ensure(program['mnemonic']==MNEMONIC and program['amount']==AMOUNT,'Test programme configuration changed.')
 l,details=calculation(r,x);ensure(l and l['eligibility_process_status']=='complete' and l['entitlement_process_status']=='complete','Native PBMS calculation is not complete.')
 ensure(len(details)==1 and details[0].get('registrant_id')==p['household_ref'],'Native calculation must contain exactly this sample household.')
 ensure(float(details[0].get('entitlement',{}).get(str(program['benefit_id']),0))==AMOUNT,'Native entitlement differs from the fixed NGN 25,000 test amount.')
 return l,program
def map_account(r,x):
 p=profile(r,x);account='JOS-DEMO-'+x['id'][-3:]
 with r.pg('example_bank_db','example-bank-postgresql') as c:
  with c.cursor() as cur:
   for acc,balance in [(TREASURY,1000000),(account,0)]:
    cur.execute("INSERT INTO accounts(account_holder_name,account_number,account_currency,account_holder_phone,account_holder_email,book_balance,available_balance,blocked_amount,created_at,updated_at,active) SELECT %s,%s,'NGN',%s,%s,%s,%s,0,now(),now(),true WHERE NOT EXISTS(SELECT 1 FROM accounts WHERE account_number=%s)",('SAMPLE JOS SIMULATOR ONLY',acc,'0000710000' if acc==TREASURY else '0000710'+x['id'][-3:],acc.lower()+'@example.invalid',balance,balance,acc))
 now=r.stamp().replace('+00:00','Z');reference=x['id']+'-MAP';payload={'request_header':{'sender_app_mnemonic':'g2p_bridge','sender_app_url':'https://bridge.openg2p.localhost','request_id':reference,'request_timestamp':now},'request_body':{'request_payload':{'transaction_id':reference,'link_request':[{'reference_id':reference,'timestamp':now,'id':p['household_ref'],'name':'SAMPLE JOS '+x['id'],'fa':{'strategy_id':5,'fa_type':'BANK','bank_name':'Local Example Bank Simulator','bank_code':'EXAMPLE_BANK','branch_name':'Synthetic branch','branch_code':'LAB','account_number':account}}]}}}
 encoded=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
 sign=requests.post(r.svc('commons-services-keymanager')+'/v1/keymanager/jwtSign',json={'id':'jos-sandbox','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':encoded,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=20);sign.raise_for_status()
 response=requests.post(r.svc('spar-openg2p-spar-mapper-api')+'/mapper/link',json=payload,headers={'Signature':sign.json()['response']['jwtSignedData']},timeout=20);response.raise_for_status();result=response.json();ensure(result['response_header']['response_status']=='SUCCESS','Signed mapper linkage failed.')
 payload['request_body']['request_payload']={'transaction_id':reference+'-RESOLVE','resolve_request':[{'reference_id':reference+'-RESOLVE','timestamp':now,'id':p['household_ref'],'fa':'','scope':'details','locale':'en'}]}
 encoded=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
 sign=requests.post(r.svc('commons-services-keymanager')+'/v1/keymanager/jwtSign',json={'id':'jos-sandbox','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':encoded,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=20);sign.raise_for_status()
 response=requests.post(r.svc('spar-openg2p-spar-mapper-api')+'/mapper/resolve',json=payload,headers={'Signature':sign.json()['response']['jwtSignedData']},timeout=20);response.raise_for_status()
 resolved=response.json()['response_body']['response_payload']['resolve_response'];ensure(len(resolved)==1,'Mapper must return exactly one household.')
 fa=resolved[0].get('fa');fa=json.loads(fa) if isinstance(fa,str) else fa
 ensure(isinstance(fa,dict) and fa.get('bank_code')=='EXAMPLE_BANK' and fa.get('account_number')==account,'Signed mapping is not the dedicated Jos simulator account.')
 return account
def operate(r,key,action,actor):
 with r.LOCK:
  x=run(r,key);p=profile(r,x);pb=r.Odoo('pbms-odoo','pbmsdb');program=r.one('SELECT * FROM programs WHERE id=?',(x['program_id'],))
  ensure(program['mnemonic']==MNEMONIC,'Wrong programme.')
  a=r.one('SELECT * FROM applications WHERE sub=? AND program=?',(x['sub'],x['program_id']))
  if action=='registry':
   if p['sync_status']!='complete':
    r.execute("UPDATE profiles SET status='approved',sync_status='pending',updated=? WHERE sub=?",(r.stamp(),x['sub']));r.sync_profile(x['sub'])
  elif action=='eligibility':
   ensure(p['status']=='approved' and p['sync_status']=='complete','Synchronise the sample registry records first.')
   if not a:
    r.execute('INSERT OR IGNORE INTO applications(sub,program,created) VALUES(?,?,?)',(x['sub'],x['program_id'],r.stamp()));a=r.one('SELECT * FROM applications WHERE sub=? AND program=?',(x['sub'],x['program_id']))
   if not a['portal_info']:r.link_portal_application(a)
   if a['status']=='pending_review':r.execute("UPDATE applications SET status='checking_eligibility' WHERE id=?",(a['id'],));r.start_eligibility(a)
  elif action=='enrol':
   ensure(a and a['pbms_list'],'Run native eligibility first.')
   listing=pb.call('g2p.beneficiary.list','read',[[a['pbms_list']]],{'fields':['beneficiary_list_id','eligibility_process_status']})[0]
   ensure(listing['eligibility_process_status']=='complete','Eligibility is still processing.')
   with r.pg('bgtaskdb','pbms-postgresql') as c:
    with c.cursor() as cur:cur.execute('SELECT registrant_details FROM beneficiary_list_details WHERE beneficiary_list_id=%s',(listing['beneficiary_list_id'],));detail=[z for chunk, in cur.fetchall() for z in chunk]
   ensure(len(detail)==1 and detail[0].get('registrant_id')==p['household_ref'],'This sample did not pass native eligibility.')
   if a['status']!='enrolled':
    pb.call('g2p.beneficiary.list','write',[[a['pbms_list']],{'list_workflow_status':'approved_final_enrolment','approval_date':str(datetime.date.today())}]);po=r.Odoo('portal-backend-odoo','portalpbmsdb');po.call('g2p.program_membership','write',[[a['portal_membership']],{'state':'enrolled'}]);po.call('g2p.program.registrant_info','write',[[a['portal_info']],{'state':'active'}]);r.execute("UPDATE applications SET status='enrolled',error=NULL WHERE id=?",(a['id'],))
  elif action=='calculate':
   ensure(a and a['status']=='enrolled','Confirm native enrolment first.')
   if not x['list_id']:
    cycles=pb.call('g2p.disbursement.cycle','search',[[['cycle_mnemonic','=',key+'-C01']]])
    cycle=cycles[0] if cycles else pb.call('g2p.disbursement.cycle','create',[{'cycle_mnemonic':key+'-C01','program_id':x['program_id'],'disbursement_schedule_date':str(datetime.date.today())}])
    listings=pb.call('g2p.beneficiary.list','search',[[['mnemonic','=','IQS-REG-APP-'+key+'-ENT-C01']]])
    lid=listings[0] if listings else pb.call('g2p.beneficiary.list','create',[{'mnemonic':'IQS-REG-APP-'+key+'-ENT-C01','disbursement_cycle_id':cycle,'iqs_household_ref':p['household_ref'],'brief':'SAMPLE JOS: fixed test NGN 25,000, no USD conversion, local simulator only','eligibility_process_status':'pending'}])
    r.execute('UPDATE jos_runs SET cycle_id=?,list_id=? WHERE id=?',(cycle,lid,key))
  elif action=='condition':
   ensure(not x['awe_id'] and not x['dispatch_started'],'Condition is frozen once payment approval is requested.');assert_calculation(r,x)
   r.execute("UPDATE jos_runs SET condition='sample_verified' WHERE id=?",(key,))
  elif action=='request_approval':
   assert_calculation(r,x);ensure(x['condition']=='sample_verified','Verify the synthetic attendance evidence first.')
   approval_row=approval(r,x)
   if not approval_row:
    session,url=awe_client(r);awe_post(session,url+'/requests',{'policy_key':POLICY,'artifact_type':'jos.synthetic.payment','artifact_id':key+'-C01','requester':'jos-synthetic-orchestrator','context':{'synthetic':True,'run_id':key,'household_ref':p['household_ref'],'program_id':x['program_id'],'cycle_id':x['cycle_id'],'list_id':x['list_id'],'amount_ngn':AMOUNT,'bank':'EXAMPLE_BANK','treasury':TREASURY,'condition':'sample_verified','requested_by':actor}});approval_row=approval(r,x)
   ensure(approval_row,'Approval request was not confirmed. Refresh; do not submit a duplicate.');r.execute('UPDATE jos_runs SET awe_id=? WHERE id=?',(approval_row['id'],key))
  elif action in ['approve','reject']:
   ar=approval(r,x);ensure(ar,'Request native AWE approval first.')
   if ar['status'] not in ['approved','rejected']:
    session,url=awe_client(r)
    for task in ar['tasks']:
     if task['status']=='open':awe_post(session,url+'/tasks/'+task['id']+'/decision',{'action':action,'comment':'SAMPLE JOS only. Staff initiator: '+actor+'. Local Example Bank; no real transfers.'})
  elif action=='dispatch':
   routing_guard(r);listing,program=assert_calculation(r,x);ar=approval(r,x);ensure(ar and ar['status']=='approved','Native AWE approval is required before dispatch.')
   expected={'synthetic':True,'run_id':key,'household_ref':p['household_ref'],'program_id':x['program_id'],'cycle_id':x['cycle_id'],'list_id':x['list_id'],'amount_ngn':AMOUNT,'bank':'EXAMPLE_BANK','treasury':TREASURY,'condition':'sample_verified'}
   ensure(all(ar['context'].get(k)==v for k,v in expected.items()),'AWE approval does not match this exact calculation.');ensure(x['condition']=='sample_verified','Synthetic condition not satisfied.')
   if x['dispatch_started'] or listing['list_workflow_status']=='approved_for_disbursement':return 'Dispatch already authorised; refresh native status. It will not be sent again.'
   with r.pg('bridge_db') as c:
    with c.cursor() as cur:cur.execute('SELECT count(*) FROM disbursements WHERE beneficiary_id=%s AND disbursement_cycle_id=%s',(p['household_ref'],x['cycle_id']));ensure(cur.fetchone()[0]==0,'An instruction already exists. Do not dispatch twice.')
   map_account(r,x)
   wid=pb.call('g2p.warehouse','search',[[['warehouse_mnemonic','=','EXAMPLE-BANK']]])[0]
   pb.upsert('g2p.warehouse.program.benefit.codes',[['program_id','=',x['program_id']],['benefit_code_id','=',program['benefit_id']]],{'warehouse_id':wid,'program_id':x['program_id'],'benefit_code_id':program['benefit_id'],'additional_info':'#ACCOUNT#'+TREASURY+'#TYPE#BANK_ACCOUNT#BRANCH#LAB'})
   # Durable intent is written before the native write. An ambiguous outcome cannot be retried blindly.
   r.execute('UPDATE jos_runs SET dispatch_started=1 WHERE id=?',(key,));event(r,key,actor,'dispatch_intent_recorded')
   pb.call('g2p.disbursement.cycle','write',[[x['cycle_id']],{'approved_for_disbursement':True}]);pb.call('g2p.beneficiary.list','write',[[x['list_id']],{'list_workflow_status':'approved_for_disbursement','approval_date':str(datetime.date.today()),'envelope_creation_status':'pending','envelope_creation_number_of_attempts':0}])
  elif action=='statement':
   routing_guard(r);ensure(x['dispatch_started'],'No native dispatch exists.')
   ensure(bank_evidence(r,key)['credited_ngn']==AMOUNT,'Wait for the local-bank credit before requesting reconciliation.')
   if not x['statement_requested']:
    r.execute('UPDATE jos_runs SET statement_requested=1 WHERE id=?',(key,));resp=requests.post(r.svc(BANK)+'/generate_account_statement',json={'program_account_number':TREASURY},timeout=20);resp.raise_for_status()
  else:raise GuardError('Unknown action.')
  event(r,key,actor,action)
 return 'Native sandbox action recorded. Refresh to observe asynchronous workers.'
def bank_evidence(r,key):
 account='JOS-DEMO-'+key[-3:]
 with r.pg('example_bank_db','example-bank-postgresql') as c:
  with c.cursor() as cur:
   cur.execute('SELECT book_balance FROM accounts WHERE account_number=%s',(account,));balance=cur.fetchone()
   cur.execute('SELECT p.payment_reference_number,p.payment_amount,b.payment_status FROM initiate_payment_requests p JOIN initiate_payment_batch_requests b USING(batch_id) WHERE p.beneficiary_account=%s AND p.remitting_account=%s',(account,TREASURY));instructions=cur.fetchall()
 return {'credited_ngn':float(balance[0]) if balance else 0,'instructions':[{'reference':v[0],'amount_ngn':v[1],'status':v[2]} for v in instructions]}
def snapshot(r):
 result={'classification':'synthetic demonstration in native services','checked_at':r.stamp(),'budget_usd':1500000,'planning_households':4250,'connected_households':3,'native_test_amount_ngn':AMOUNT,'exchange_rate_assumed':False,'rows':[],'limitations':['Three connected fictional households, separate from 4,250 planning records.','NGN 25,000 is a fixed sandbox test amount, not a conversion of the proposed USD benefit.','Registry synchronisation uses the existing custom lab adapter. No NASSCO or NIMC connection.','AWE decisions use the existing sandbox integration administrator; initiating staff is separately audited. Production separation of duties is not claimed.','Synthetic attendance is recorded by the Jos adapter; no school-system integration. No real funds or external payment rail.','Geography is Plateau state only until Jos LGA/ward mappings are validated.']}
 for key in IDS:
  x=run(r,key);p=profile(r,x);a=r.one('SELECT * FROM applications WHERE sub=? AND program=?',(x['sub'],x['program_id']));ar=approval(r,x);l,detail=calculation(r,x)
  row={'id':key,'name':json.loads(p['data'])['household_name'],'household_ref':p['household_ref'],'registry_status':p['sync_status'],'registry_mapping':json.loads(p['mapping']) if p['mapping'] else {},'application_status':a['status'] if a else 'not started','enrolment_list_id':a['pbms_list'] if a else None,'program_id':x['program_id'],'cycle_id':x['cycle_id'],'list_id':x['list_id'],'calculation':l,'condition':x['condition'],'awe':{k:ar[k] for k in ['id','status','tasks']} if ar else None,'dispatch_started':bool(x['dispatch_started']),'statement_requested':bool(x['statement_requested']),'bank':bank_evidence(r,key),'bridge':[],'events':r.rows('SELECT actor,action,at FROM jos_events WHERE run_id=? ORDER BY id',(key,))}
  with r.pg('register') as c:
   with c.cursor() as cur:cur.execute('SELECT internal_record_id FROM g2p_register_households WHERE functional_record_id=%s',(p['household_ref'],));found=cur.fetchone();row['modern_registry_id']=found[0] if found else None
  if x['cycle_id']:
   with r.pg('bridge_db') as c:
    with c.cursor() as cur:
     cur.execute('SELECT d.id,d.disbursement_envelope_id,d.disbursement_quantity,b.fa_resolution_status,b.sponsor_bank_dispatch_status,b.sponsor_bank_dispatch_latest_error_code FROM disbursements d LEFT JOIN disbursement_batch_control b ON b.id=d.disbursement_batch_control_id WHERE d.beneficiary_id=%s AND d.disbursement_cycle_id=%s',(p['household_ref'],x['cycle_id']))
     for v in cur.fetchall():
      cur.execute('SELECT remittance_statement_id,remittance_entry_date,reversal_found FROM disbursement_recons WHERE disbursement_id=%s',(v[0],));recons=cur.fetchall();row['bridge'].append({'instruction_id':v[0],'envelope_id':v[1],'amount_ngn':v[2],'mapping_status':v[3],'dispatch_status':v[4],'error':v[5],'reconciliations':[{'statement_id':z[0],'date':str(z[1]),'reversed':z[2]} for z in recons]})
  result['rows'].append(row)
 return result
def public_snapshot(data):
 # Whitelist only the fixed synthetic cohort; no credentials, bank accounts or general registry data.
 out={k:data[k] for k in ['classification','checked_at','budget_usd','planning_households','connected_households','native_test_amount_ngn','exchange_rate_assumed','limitations']};out['rows']=[]
 for row in data['rows']:
  out['rows'].append({k:row[k] for k in ['id','name','household_ref','registry_status','modern_registry_id','program_id','cycle_id','list_id','application_status','condition','awe','dispatch_started','statement_requested','bank','bridge']})
 return out
def publish(r,data):
 for folder in ['public-home','home']:
  path=Path('/opt/openg2p-lab')/folder/'jos-cct/connected.json'
  if path.parent.exists():
   tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(public_snapshot(data),default=str));tmp.chmod(0o644);tmp.replace(path)
def install(r):
 init(r);bp=Blueprint('jos_connected',__name__)
 @bp.get(r.PREFIX+'/jos-cct')
 def home():
  if not g.user:return redirect(r.PREFIX+'/login?mode=staff&jos=1')
  r.require_staff();data=snapshot(r);publish(r,data);return r.page('jos-connected.html',data=data,message=request.args.get('message',''))
 @bp.get(r.PREFIX+'/jos-cct/minister')
 def minister():
  if not g.user:return redirect(r.PREFIX+'/login?mode=staff&jos=1&minister=1')
  r.require_staff();key=request.args.get('sample','JOS-NATIVE-002')
  if key not in IDS:abort(404)
  try:step=int(request.args.get('step','1'))
  except ValueError:abort(400)
  if step not in range(1,9):abort(400)
  data=snapshot(r);publish(r,data);row=next(x for x in data['rows'] if x['id']==key)
  stages=[minister_stage(row,n) for n in range(1,9)]
  return r.page('jos-minister.html',data=data,row=row,stage=stages[step-1],stages=stages,panel=request.args.get('panel')=='1',message=request.args.get('message',''),error=request.args.get('error')=='1')
 @bp.get(r.PREFIX+'/api/jos-cct')
 def api():r.require_user();r.require_staff();return snapshot(r)
 @bp.post(r.PREFIX+'/jos-cct/<key>/<action>')
 def act(key,action):
  r.require_user();r.require_staff()
  try:message=operate(r,key,action,g.user['sub'])
  except GuardError as e:
   if request.form.get('minister')=='1' and key in IDS:
    return redirect(r.PREFIX+'/jos-cct/minister?sample='+key+'&step='+str(max(1,min(8,request.form.get('step',1,type=int) or 1)))+'&error=1&message='+requests.utils.quote(str(e)))
   abort(409,str(e))
  if request.form.get('minister')=='1':
   return redirect(r.PREFIX+'/jos-cct/minister?sample='+key+'&step='+str(max(1,min(8,request.form.get('step',1,type=int) or 1)))+'&message='+requests.utils.quote(message))
  return redirect(r.PREFIX+'/jos-cct?message='+requests.utils.quote(message))
 r.app.register_blueprint(bp)
# Presentation metadata is derived from native evidence; it never performs an operation.
def minister_stage(row,step):
 b=row['bridge'][0] if row['bridge'] else {};ar=row['awe'] or {};calc=row['calculation'] or {}
 matched=any(not z['reversed'] for x in row['bridge'] for z in x['reconciliations'])
 done=[row['registry_status']=='complete',row['application_status']=='enrolled',calc.get('eligibility_process_status')=='complete' and calc.get('entitlement_process_status')=='complete',row['condition']=='sample_verified',ar.get('status')=='approved',b.get('dispatch_status')=='PROCESSED',row['bank']['credited_ngn']==AMOUNT,matched]
 titles=['Registration','Eligibility and enrolment','Benefit calculation','Sample attendance','Payment approval','Signed mapping and dispatch','Simulator payment receipt','Statement reconciliation']
 services=['Registry','PBMS','PBMS','Jos conditions adapter','AWE','SPAR and Bridge','Local Example Bank','Bridge reconciliation']
 explanations=['Approve the fictional intake and synchronise its household reference across the connected registries.','Run eligibility for this sample, wait for native processing, then confirm enrolment.','Create the one-household native entitlement and wait for calculation completion. The fixed test amount is NGN 25,000, not a USD conversion.','Record fictional attendance: 18 of 20 school days. This illustrative 80% test gates the whole amount; no school system is connected.','Request and then approve the native AWE task. The sandbox integration administrator executes decisions and the initiating staff user is audited separately.','Validate the signed sample account mapping and authorise Bridge to dispatch only to the local Example Bank. Duplicate authorisation is blocked.','Wait for the native simulator credit. A submitted instruction is not yet proof of receipt. No real account or money is involved.','Request the simulator statement and wait for the native matching result. A reversed record does not count as reconciled.']
 actions=[]
 if not done[step-1] and (step==1 or all(done[:step-1])):
  if step==1:actions=[('registry','Approve sample registration and synchronise')]
  elif step==2:actions=[('eligibility','Run native eligibility')] if row['application_status']=='not started' else [('enrol','Confirm native enrolment')]
  elif step==3 and not row['list_id']:actions=[('calculate','Calculate sample benefit')]
  elif step==4:actions=[('condition','Verify fictional attendance')]
  elif step==5 and not ar:actions=[('request_approval','Request native AWE approval')]
  elif step==5 and ar.get('status') not in ['approved','rejected']:actions=[('approve','Approve sample in native AWE'),('reject','Reject sample in native AWE')]
  elif step==6 and not row['dispatch_started']:actions=[('dispatch','Authorise simulated payment — NGN 25,000')]
  elif step==8 and not row['statement_requested']:actions=[('statement','Request simulator statement')]
 base='/registration/jos-cct/minister?sample='+row['id']+'&step='+str(step)
 dashboard=base+'&panel=1'
 if step==1:
  partner=row['registry_mapping'].get('socialregistrydb',{}).get('household')
  dashboard='https://g2p-registry.wverve.in/web?_nsipa_records=1'+('#id='+str(partner)+'&model=res.partner&view_type=form' if partner else '#action=188')
 elif step in [2,3]:
  lid=row['enrolment_list_id'] if step==2 else row['list_id']
  dashboard='https://g2p-pbms.wverve.in/web?_nsipa_records=1#id='+str(lid or row['program_id'])+'&model='+('g2p.beneficiary.list' if lid else 'g2p.program.definition')+'&view_type=form'
 elif step==5:dashboard='https://g2p-awe.wverve.in/requests?_nsipa_records=1'
 return dict(number=step,title=titles[step-1],service=services[step-1],explanation=explanations[step-1],done=done[step-1],all_done=all(done),prerequisites=all(done[:step-1]),actions=actions,url=base,dashboard=dashboard,native_ui=step in [1,2,3,5])
