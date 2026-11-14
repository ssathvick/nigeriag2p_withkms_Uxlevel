"""Add deterministic synthetic fixtures without deleting or overwriting existing records."""
import pathlib,sys,json,subprocess,uuid,csv,xmlrpc.client,yaml,requests,datetime,time
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
root=pathlib.Path('/opt/openg2p-lab');workspace=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
tag='IQS-SYN-20261003'; password=yaml.safe_load((root/'credentials.yaml').read_text())['admin_password']
report={};now='2026-10-03 09:00:00'
def sid(value):return str(uuid.uuid5(uuid.NAMESPACE_URL,tag+'/'+value))
def q(value):
 if value is None:return 'NULL'
 if isinstance(value,bool):return 'true' if value else 'false'
 if isinstance(value,(int,float)):return str(value)
 return "'"+str(value).replace("'","''")+"'"
def insert(table,data,key):return f"INSERT INTO {table}({','.join(data)}) VALUES({','.join(q(v) for v in data.values())}) ON CONFLICT({key}) DO NOTHING;"
def svc(name):return 'http://'+subprocess.check_output(['kubectl','get','svc',name,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
class Odoo:
 def __init__(self,service,db):
  url=svc(service);self.db=db;self.uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(db,'admin@nigeria.openg2p.localhost',password,{})
  if not self.uid:raise RuntimeError('Odoo authentication: '+db)
  self.proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
 def call(self,model,method,args,kw=None):return self.proxy.execute_kw(self.db,self.uid,password,model,method,args,kw or {})
 def create(self,model,domain,values):
  ids=self.call(model,'search',[domain]);return ids[0] if ids else self.call(model,'create',[values])
 def bulk(self,model,rows):
  existing=self.call(model,'search_read',[[['ref','like',tag+'%']]],{'fields':['ref']})
  refs={r['ref'] for r in existing};new=[r for r in rows if r['ref'] not in refs]
  if new:self.call(model,'create',[new])
  return {r['ref']:r['id'] for r in self.call(model,'search_read',[[['ref','like',tag+'%']]],{'fields':['ref']})}
states=[line.split('|') for line in query('master_data',"SELECT level_value_id,level_value_mnemonic FROM g2p_geo_level_values WHERE length(level_value_id)=4 AND level_value_id LIKE 'NG%' ORDER BY level_value_id;").splitlines()]
assert len(states)==37
first=['Amina','Chinedu','Zainab','Tunde','Ngozi','Musa','Blessing','Ibrahim','Ada','Emeka','Hauwa','Yusuf','Funke','Umar','Grace','Babatunde','Maryam','Chisom','Esther','Sani']
last=['Okafor','Abubakar','Adeyemi','Ibrahim','Eze','Bello','Nwosu','Lawal','Ojo','Usman']
people=[];households=[];sql=[]
for h in range(50):
 ref=f'{tag}-HH-{h+1:04d}';geo,state=states[h%37];head_ref=f'{tag}-I-{h*4+1:04d}'
 households.append({'ref':ref,'name':f'Synthetic Household {h+1:03d} — {state}','state':state,'geo':geo})
 sql.append(insert('g2p_register_households',{'internal_record_id':sid(ref),'functional_record_id':ref,'record_name':households[-1]['name'],'created_by':'iqs-synthetic-batch','created_at':now,'last_approved_at':now,'last_approved_by':'iqs-synthetic-batch','record_status':'ACTIVE','search_text':households[-1]['name'],'household_head_internal_record_id':sid(head_ref),'household_head_name':f'{first[(h*4)%20]} {last[h%10]} Demo {h*4+1:03d}','size_total':4,'size_adults':2,'country_code':'NGA','geo_lowest_level_value_id':geo},'internal_record_id'))
 for member in range(4):
  n=h*4+member+1;ref=f'{tag}-I-{n:04d}';given=first[(n-1)%20];family=last[h%10];name=f'{given} {family} Demo {n:03d}';year=[1975+h%20,1978+h%20,2009+h%7,2014+h%5][member]
  person={'ref':ref,'household_ref':households[-1]['ref'],'name':name,'given':given,'family':family,'birth_date':f'{year}-'+f'{n%12+1:02d}-15','gender':'Female' if member%2==0 else 'Male','state':state,'geo':geo,'email':f'iqs-demo-{n:04d}@example.invalid','occupation':['Trader','Farmer','Student','Student'][member],'income':45000+(h%8)*15000 if member<2 else 0}
  people.append(person)
  sql.append(insert('g2p_register_individuals',{'internal_record_id':sid(ref),'functional_record_id':ref,'link_internal_record_id':sid(person['household_ref']),'record_name':name,'created_by':'iqs-synthetic-batch','created_at':now,'last_approved_at':now,'last_approved_by':'iqs-synthetic-batch','record_status':'ACTIVE','search_text':name+' '+ref+' '+state,'foundational_id':'LAB-ID-'+f'{n:06d}','first_name':given,'last_name':family,'given_name':given,'full_name':name,'gender':person['gender'],'birth_date':person['birth_date'],'country_code':'NGA','geo_lowest_level_value_id':geo,'occupation':person['occupation'],'address_line_1':f'Synthetic Demo Street {h+1:03d}','address_line_2':'Fictional UX test address'},'internal_record_id'))
query('register','BEGIN;\n'+'\n'.join(sql)+'\nCOMMIT;')
report['modern_registry']={'individuals':200,'households':50,'states_and_fct':37};print('Modern registry: 200 individuals and 50 households ready.',flush=True)
for service,db in [('registry-odoo','socialregistrydb'),('portal-backend-odoo','portalpbmsdb')]:
 o=Odoo(service,db);country=o.call('res.country','search',[[['code','=','NG']]])[0]
 rows=[{'name':h['name'],'ref':h['ref'],'is_registrant':True,'is_group':True,'country_id':country,'company_id':1,'comment':'IQS synthetic UX batch. No real household.'} for h in households]
 rows += [{'name':p['name'],'given_name':p['given'],'family_name':p['family']+' Demo '+p['ref'][-4:],'ref':p['ref'],'is_registrant':True,'is_group':False,'country_id':country,'company_id':1,'birthdate':p['birth_date'],'email':p['email'],'gender':p['gender'],'city':p['state'],'street':'Synthetic Demo Street','comment':'IQS synthetic UX batch. No real person, phone, NIN or bank account.'} for p in people]
 if db=='socialregistrydb':
  for gender in ['Female','Male']:
   o.create('gender.type',[['value','=',gender]],{'value':gender,'code':gender})
 ids=o.bulk('res.partner',rows)
 fields=o.call('g2p.group.membership','fields_get',[],{'attributes':['relation']})
 group_key=next(k for k,v in fields.items() if v.get('relation')=='res.partner' and 'group' in k)
 member_key=next(k for k,v in fields.items() if v.get('relation')=='res.partner' and ('individual' in k or 'member' in k))
 for p in people:
  values={group_key:ids[p['household_ref']],member_key:ids[p['ref']]}
  o.create('g2p.group.membership',[[k,'=',v] for k,v in values.items()],values)
 report[db]={'individuals':200,'households':50,'memberships':200};print(db+': people, households and membership links ready.',flush=True)
 if db=='portalpbmsdb':portal=o;portal_ids=ids
pbms=Odoo('pbms-odoo','pbmsdb')
programmes=[('HOUSEHOLD','Household Cash Support',25000,'ACTIVE'),('FARM','Smallholder Farming Grant',40000,'ACTIVE'),('SCHOOL','School Materials Support',15000,'ACTIVE'),('LIVELIHOOD','Livelihood Starter Grant',50000,'PAUSED'),('RELIEF','Emergency Relief Assistance',30000,'CLOSED')]
for code,label,amount,status in programmes:
 mnemonic=tag+'-'+code
 benefit=pbms.create('g2p.benefit.codes',[['benefit_mnemonic','=',mnemonic]],{'benefit_mnemonic':mnemonic,'benefit_type':'CASH_DIGITAL','benefit_description':label+' — Synthetic UX fixture; no live funding.','measurement_unit':'NGN'})
 program=pbms.create('g2p.program.definition',[['program_mnemonic','=',mnemonic]],{'program_mnemonic':mnemonic,'description':label+' — IQS Synthetic Demo','target_registry':'farmer','program_status':status,'enrollment_frequency':'OnDemand','disbursement_frequency':'OnDemand','beneficiary_list':'latest_always'})
 pbms.create('g2p.program.benefit.codes',[['program_id','=',program],['benefit_code_id','=',benefit]],{'program_id':program,'benefit_code_id':benefit,'max_quantity':amount})
 pbms.create('g2p.enrollment.cycle',[['cycle_mnemonic','=',mnemonic+'-C01']],{'cycle_mnemonic':mnemonic+'-C01','cycle_number':1,'program_id':program,'enrollment_start_date':'2026-10-01','enrollment_end_date':'2026-12-31','disbursement_start_date':'2026-10-01','disbursement_end_date':'2026-12-31'})
existing={r['link_registry_id'] for r in pbms.call('g2p.farmer.registry','search_read',[[['link_registry_id','like',tag+'%']]],{'fields':['link_registry_id']})}
farmers=[{'link_registry_id':p['ref'],'name':p['name'],'gender':p['gender'].lower(),'land_area':round(0.5+(i%10)*0.4,1),'annual_income':p['income']*12,'large_area_code':p['state'],'small_area_code':'Synthetic Demo Community'} for i,p in enumerate(people) if p['ref'] not in existing]
if farmers:pbms.call('g2p.farmer.registry','create',[farmers])
report['pbms']={'programmes':5,'benefit_codes':5,'enrollment_cycles':5,'fixture_registry_rows':200};print('PBMS programmes, NGN benefits, cycles and 200 fixture rows ready.',flush=True)
schema={'display':'form','components':[{'type':'htmlelement','tag':'p','content':'IQS synthetic UX demonstration only. Do not enter real personal information.','key':'notice','input':False},{'type':'textfield','label':'Demo contact name','key':'contactName','input':True},{'type':'textarea','label':'Demo support request','key':'supportRequest','input':True},{'type':'checkbox','label':'This is a synthetic demonstration','key':'demoConsent','input':True},{'type':'button','label':'Submit application','key':'submit','action':'submit','input':True}]}
builder=portal.create('formio.builder',[['name','=',tag]],{'name':tag,'title':'IQS Synthetic Support Application','schema':json.dumps(schema),'portal':True,'state':'CURRENT','formio_version_id':portal.call('formio.version','search',[[]])[0]})
portal_programs=[]
for code,label,amount,status in programmes:
 portal_programs.append(portal.create('g2p.program',[['name','=',label+' — IQS Synthetic Demo']],{'name':label+' — IQS Synthetic Demo','description':'Synthetic local UX fixture. Sample benefit: NGN '+str(amount)+'. No government policy or live payment.','active':True,'target_type':'individual','portal_form_builder_id':builder}))
membership_states=['draft','enrolled','paused','not_eligible','exited']
for i,p in enumerate(people):
 state=membership_states[(i//5)%5];program=portal_programs[i%5];partner=portal_ids[p['ref']]
 portal.create('g2p.program_membership',[['partner_id','=',partner],['program_id','=',program]],{'partner_id':partner,'program_id':program,'state':state,'company_id':1})
 portal.create('formio.form',[['uuid','=',sid('application/'+p['ref'])]],{'uuid':sid('application/'+p['ref']),'title':'Synthetic Application '+p['ref'],'builder_id':builder,'partner_id':partner,'submission_data':json.dumps({'contactName':p['name'],'supportRequest':'Synthetic support request for '+programmes[i%5][1],'demoConsent':True}),'state':'DRAFT' if state=='draft' else 'COMPLETE','submission_date':now})
fatima=portal.call('res.partner','search',[[['ref','=','NG-PORTAL-0001']]])[0]
for i,program in enumerate(portal_programs):portal.create('g2p.program_membership',[['partner_id','=',fatima],['program_id','=',program]],{'partner_id':fatima,'program_id':program,'state':membership_states[i],'company_id':1})
report['beneficiary_portal']={'programmes':5,'application_forms':200,'programme_memberships':205,'demo_login':'fatima','states':membership_states};print('Beneficiary programmes, 200 applications and varied memberships ready.',flush=True)
# Reuse existing administrator access; do not create new users or broaden roles.
kc=svc('commons-keycloak')
master=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);master.raise_for_status()
ks=requests.Session();ks.headers['Authorization']='Bearer '+master.json()['access_token']
client=ks.get(kc+'/admin/realms/staff/clients',params={'clientId':'awe-admin-portal'}).json()[0]
secret=ks.get(kc+'/admin/realms/staff/clients/'+client['id']+'/client-secret').json().get('value','')
token=requests.post(kc+'/realms/staff/protocol/openid-connect/token',data={'client_id':'awe-admin-portal','client_secret':secret,'grant_type':'password','username':'admin','password':password},timeout=20);token.raise_for_status()
session=requests.Session();session.headers['Authorization']='Bearer '+token.json()['access_token']
pm=svc('commons-services-pm-staff-portal-api')
def api(method,url,payload=None):
 for attempt in range(4):
  r=session.request(method,url,json=payload,timeout=30)
  if not (r.status_code==404 and '/tasks/' in url and attempt<3):break
  time.sleep(0.5)
 if not r.ok:raise RuntimeError(str(r.status_code)+' '+r.text[:600])
 return r.json() if r.content else {}
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
partner_names=['Demo Field Registration Team','Demo Document Verification Service','Demo Payment Adapter','Demo Grievance Support Desk','Demo Programme Analytics','Demo Community Outreach','Demo School Support Team','Demo Agricultural Support Team','Demo Consent Integrator','Demo Legacy Integration']
existing_pm=set(query('partner_management',"SELECT partner_id FROM pm_partners WHERE partner_id LIKE '"+tag+"%';").splitlines())
for i,name in enumerate(partner_names):
 pid=f'{tag}-PARTNER-{i+1:02d}'
 if pid in existing_pm:continue
 key=rsa.generate_private_key(public_exponent=65537,key_size=2048).public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
 request=api('POST',pm+'/partners/requests/onboarding',{'partner_id':pid,'name':name,'org_name':'IQS Synthetic Lab Organisation '+str(i+1),'description':'Synthetic UX fixture only. No external integration.','keys':[{'public_key':key,'kid':pid+'-demo-key','algorithm':'RS256'}]})
 api('POST',pm+'/partners/requests/'+request['id']+'/approve',{'notes':'Synthetic fixture approval; no external connection.'})
 if i>=8:api('POST',pm+'/partners/'+pid+'/disable')
for i in range(6):
 pid=f'{tag}-REVIEW-{i+1:02d}'
 if query('partner_management',"SELECT id FROM pm_partner_requests WHERE partner_id="+q(pid)+';').strip():continue
 key=rsa.generate_private_key(public_exponent=65537,key_size=2048).public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
 request=api('POST',pm+'/partners/requests/onboarding',{'partner_id':pid,'name':'Synthetic Pending Partner '+str(i+1),'org_name':'IQS Synthetic Review Organisation','description':'Synthetic onboarding review fixture.','keys':[{'public_key':key,'kid':pid+'-demo-key','algorithm':'RS256'}]})
 if i>=4:api('POST',pm+'/partners/requests/'+request['id']+'/reject',{'notes':'Synthetic rejection for UI status testing.'})
report['partner_management']={'partners':10,'active':8,'disabled':2,'extra_pending_requests':4,'extra_rejected_requests':2};print('Partner Management: 10 partners and 6 additional review requests ready.',flush=True)
# AWE has its own client-scoped roles. Obtain a token using its already-enabled lab client.
master=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);master.raise_for_status()
ks=requests.Session();ks.headers['Authorization']='Bearer '+master.json()['access_token']
client=ks.get(kc+'/admin/realms/staff/clients',params={'clientId':'awe-admin-portal'}).json()[0]
secret=ks.get(kc+'/admin/realms/staff/clients/'+client['id']+'/client-secret').json().get('value','')
token=requests.post(kc+'/realms/staff/protocol/openid-connect/token',data={'client_id':'awe-admin-portal','client_secret':secret,'grant_type':'password','username':'admin','password':password},timeout=20);token.raise_for_status()
session.headers['Authorization']='Bearer '+token.json()['access_token'];awe=svc('commons-services-awe')+'/v1/awe';policy=tag+'.synthetic-review'
if not query('awe','SELECT id FROM approval_policy WHERE policy_key='+q(policy)+';').strip():
 api('POST',awe+'/policies',{'policy_key':policy,'name':'IQS Synthetic Application Review','description':'Standalone synthetic approval examples; no registry callback or live eligibility decision.','artifact_type':'iqs.synthetic_demo','stages':[{'name':'Demo review','stage_order':1,'mode':'all','rules':[{'rule_type':'user','rule_value':{'user_id':'admin'}}]}]})
 api('POST',awe+'/policies/'+policy+'/versions/1/activate')
for i in range(15):
 artifact=f'{tag}-AWE-{i+1:02d}'
 existing=query('awe','SELECT id FROM approval_request WHERE artifact_id='+q(artifact)+';').strip()
 if existing:
  request={'tasks':[{'id':t} for t in query('awe','SELECT id FROM approval_task WHERE request_id='+q(existing)+" AND status='open';").splitlines()]}
 else:
  request=api('POST',awe+'/requests',{'policy_key':policy,'artifact_type':'iqs.synthetic_demo','artifact_id':artifact,'requester':'iqs-synthetic-fixture','context':{'synthetic':True,'beneficiary_name':people[i]['name'],'reference':people[i]['ref'],'state':people[i]['state'],'programme':programmes[i%5][1]}})
 if i>=5:
  for task in request.get('tasks',[]):api('POST',awe+'/tasks/'+task['id']+'/decision',{'action':'approve' if i<10 else 'reject','comment':'Synthetic status example for UX testing.'})
report['approvals']={'policy':1,'requests':15,'pending':5,'approved':5,'rejected':5};print('Approval Workflow Engine: 15 genuine synthetic workflow requests ready.',flush=True)
bundle={'batch':tag,'synthetic':True,'people':people,'households':households,'programmes':[{'code':c,'name':n,'ngn_amount':a,'status':s} for c,n,a,s in programmes],'report':report}
out=workspace/'synthetic-data';out.mkdir(exist_ok=True)
(out/'platform-batch.json').write_text(json.dumps(bundle,indent=2,ensure_ascii=False))
with (out/'individuals.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(people[0]));writer.writeheader();writer.writerows(people)
(root/'synthetic-platform-batch.json').write_text(json.dumps(bundle,indent=2,ensure_ascii=False))
(out/'summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
