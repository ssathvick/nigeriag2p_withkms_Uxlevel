"""IQS synthetic sandbox intake and PBMS integration. No payment instructions."""
import os,json,sqlite3,secrets,time,uuid,hashlib,base64,threading,subprocess,datetime,xmlrpc.client,logging,fcntl
from pathlib import Path
from urllib.parse import urlencode
import requests,yaml,jwt,psycopg2
import nigeria_geography
import knowledge_management
import local_ai
from psycopg2 import sql
from flask import Flask,request,redirect,render_template,abort,g

ROOT=Path(os.environ.get('IQS_REGISTRATION_ROOT','/opt/openg2p-lab/registration'))
ROOT.mkdir(parents=True,exist_ok=True);CONFIG=json.loads((ROOT/'config.json').read_text())
BASE=CONFIG['base_url'];PREFIX='/registration'
class IntegrationLock:
 def __init__(self):self.local=threading.RLock();self.depth=0;self.fd=None
 def __enter__(self):
  self.local.acquire()
  if self.depth==0:self.fd=open(ROOT/'integration.lock','a');fcntl.flock(self.fd,fcntl.LOCK_EX)
  self.depth+=1
 def __exit__(self,*args):
  self.depth-=1
  if self.depth==0:fcntl.flock(self.fd,fcntl.LOCK_UN);self.fd.close()
  self.local.release()
LOCK=IntegrationLock()
app=Flask(__name__,template_folder=str(ROOT/'templates'),static_folder=str(ROOT/'static'),static_url_path=PREFIX+'/static')
app.config['MAX_CONTENT_LENGTH']=60000
logging.basicConfig(level=logging.INFO)
def db():
 c=sqlite3.connect(ROOT/'intake.sqlite',timeout=30);c.row_factory=sqlite3.Row;c.execute('PRAGMA journal_mode=WAL');return c
def execute(q,args=()):
 with db() as c:return c.execute(q,args).lastrowid
def rows(q,args=()):
 with db() as c:return [dict(r) for r in c.execute(q,args)]
def one(q,args=()):
 r=rows(q,args);return r[0] if r else None
with db() as c:
 c.executescript('''
 CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,data TEXT,expires INTEGER);
 CREATE TABLE IF NOT EXISTS profiles(sub TEXT PRIMARY KEY,ref TEXT UNIQUE,household_ref TEXT UNIQUE,data TEXT,status TEXT DEFAULT 'pending_review',sync_status TEXT DEFAULT 'not_started',error TEXT,portal_partner INTEGER,mapping TEXT,updated TEXT);
 CREATE TABLE IF NOT EXISTS programs(id INTEGER PRIMARY KEY,mnemonic TEXT UNIQUE,name TEXT,amount REAL,max_income REAL,min_members INTEGER,portal_id INTEGER,cycle_id INTEGER,benefit_id INTEGER,status TEXT DEFAULT 'ACTIVE');
 CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT,sub TEXT,program INTEGER,status TEXT DEFAULT 'pending_review',portal_info INTEGER,portal_membership INTEGER,pbms_list INTEGER,error TEXT,created TEXT,UNIQUE(sub,program));
 CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,actor TEXT,action TEXT,reference TEXT,at TEXT);
 ''')
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
with db() as c:
 if 'last_editor' not in {row[1] for row in c.execute('PRAGMA table_info(profiles)')}:
  c.execute('ALTER TABLE profiles ADD COLUMN last_editor TEXT')
def audit(action,reference):execute('INSERT INTO audit(actor,action,reference,at) VALUES(?,?,?,?)',(g.user.get('sub','system') if hasattr(g,'user') else 'system',action,str(reference),stamp()))
def is_maker(profile,actor):
 return profile['sub']==actor or profile.get('last_editor')==actor or bool(one("SELECT id FROM audit WHERE actor=? AND reference IN (?,?) AND action IN ('registration_submitted','officer_corrected_and_resubmitted') LIMIT 1",(actor,profile['sub'],profile['household_ref'])))
def svc(name):
 return 'http://'+subprocess.check_output(['kubectl','-n','nigeria','get','svc',name,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
class Odoo:
 def __init__(self,service,database):
  url=svc(service);self.database=database;self.password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
  self.uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(database,'admin@nigeria.openg2p.localhost',self.password,{})
  if not self.uid:raise RuntimeError('Backend authentication unavailable')
  self.proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object',allow_none=True)
 def call(self,model,method,args,kw=None):return self.proxy.execute_kw(self.database,self.uid,self.password,model,method,args,kw or {})
 def upsert(self,model,domain,values):
  ids=self.call(model,'search',[domain])
  if ids:self.call(model,'write',[ids[:1],values]);return ids[0]
  return self.call(model,'create',[values])
def pg(database,service='commons-postgresql'):
 s=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret',service,'-o','json']))
 return psycopg2.connect(host=svc(service)[7:],dbname=database,user='postgres',password=base64.b64decode(s['data']['postgres-password']).decode(),connect_timeout=10)
def upsert_pg(cur,table,data,key):
 columns=list(data);updates=[k for k in columns if k!=key]
 cur.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({}) ON CONFLICT ({}) DO UPDATE SET {}').format(sql.Identifier(table),sql.SQL(',').join(map(sql.Identifier,columns)),sql.SQL(',').join(sql.Placeholder() for _ in columns),sql.Identifier(key),sql.SQL(',').join(sql.SQL('{}=EXCLUDED.{}').format(sql.Identifier(k),sql.Identifier(k)) for k in updates)),list(data.values()))
def issuer(mode):return CONFIG['keycloak']+'/realms/'+('staff' if mode=='staff' else 'beneficiary')
@app.before_request
def context():
 if request.path.endswith('/health'):return
 sid=request.cookies.get('IQS-INTAKE');s=one('SELECT * FROM sessions WHERE id=? AND expires>?',(sid or '',int(time.time())))
 g.session=json.loads(s['data']) if s else {};g.sid=sid if s else secrets.token_urlsafe(32);g.user=g.session.get('user',{})
 g.session.setdefault('csrf',secrets.token_urlsafe(32));g.staff=g.session.get('mode')=='staff' and 'iqs-intake-reviewer' in g.user.get('roles',[])
 if request.method=='POST' and not secrets.compare_digest(request.form.get('csrf',''),g.session['csrf']):abort(403,'Session expired. Reload the page and try again.')
@app.after_request
def cookies(res):
 if hasattr(g,'session'):
  execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',(g.sid,json.dumps(g.session),int(time.time())+3600))
  res.set_cookie('IQS-INTAKE',g.sid,max_age=3600,secure=True,httponly=True,samesite='Lax',path=PREFIX)
 res.headers['Cache-Control']='no-store';res.headers['X-Content-Type-Options']='nosniff';res.headers['X-Frame-Options']='DENY';res.headers['Referrer-Policy']='same-origin'
 return res
def require_user():
 if not g.user:abort(401,'Please sign in first.')
def require_staff():
 if not g.staff and not getattr(g,'workspace_verification_authorized',False):abort(403,'Staff reviewer access is required.')
def page(name,**kw):return render_template(name,user=g.user,staff=g.staff,csrf=g.session['csrf'],base=BASE,prefix=PREFIX,**kw)
@app.get(PREFIX+'/mobile')
def mobile_information():return page('mobile.html')
@app.get(PREFIX+'/health')
def health():return {'status':'ok','service':'IQS registration integration'}
@app.get(PREFIX+'/login')
def login():
 mode='staff' if request.args.get('mode')=='staff' else 'beneficiary';state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(48);nonce=secrets.token_urlsafe(32)
 g.session['login']={'mode':mode,'state':state,'verifier':verifier,'nonce':nonce,'at':int(time.time()),'workspace':request.args.get('workspace')=='1','geography':request.args.get('geography')=='1','knowledge':request.args.get('knowledge')=='1','analytics':request.args.get('analytics')=='1','simulation':request.args.get('simulation')=='1','ai':request.args.get('ai')=='1','ai_module':request.args.get('module','platform')[:80],'ai_stage':request.args.get('stage','')[:160]}
 g.session['login']['jos']=request.args.get('jos')=='1'
 g.session['login']['jos_minister']=request.args.get('minister')=='1'
 g.session['login']['phase1']=request.args.get('phase1')=='1'
 g.session['login']['dashboard_service']=request.args.get('service','overview')[:80]
 g.session['login']['records']=request.args.get('_nsipa_records')=='1' or '_nsipa_records=1' in (request.referrer or '')
 g.session['login']['grievances']=request.args.get('grievances')=='1'
 client=CONFIG['clients'][mode];params={'client_id':client['id'],'response_type':'code','scope':'openid profile email','redirect_uri':BASE+PREFIX+'/callback','state':state,'nonce':nonce,'code_challenge':base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('='),'code_challenge_method':'S256'}
 endpoint='registrations' if request.args.get('signup')=='1' and mode=='beneficiary' else 'auth'
 return redirect(issuer(mode)+'/protocol/openid-connect/'+endpoint+'?'+urlencode(params))
def default_login_destination(mode,roles):
 if mode!='staff':return PREFIX+'/analytics?service=beneficiary'
 if {'iqs-intake-reviewer','iqs-programme-supervisor','iqs-registration-officer','iqs-verification-officer'} & set(roles):return PREFIX+'/analytics'
 return PREFIX+'/workspace'
@app.get(PREFIX+'/callback')
def callback():
 flow=g.session.pop('login',{})
 if not flow or not secrets.compare_digest(flow['state'],request.args.get('state','')) or time.time()-flow['at']>600:abort(400,'Invalid or expired sign-in request.')
 if request.args.get('error'):abort(400,'Sign-in was cancelled. Return to registration and try again.')
 client=CONFIG['clients'][flow['mode']];iss=issuer(flow['mode'])
 r=requests.post(iss+'/protocol/openid-connect/token',data={'grant_type':'authorization_code','code':request.args.get('code'),'client_id':client['id'],'client_secret':client['secret'],'redirect_uri':BASE+PREFIX+'/callback','code_verifier':flow['verifier']},timeout=20);r.raise_for_status()
 tokens=r.json();jwks=requests.get(iss+'/protocol/openid-connect/certs',timeout=20);jwks.raise_for_status()
 kid=jwt.get_unverified_header(tokens['id_token']).get('kid');key=jwt.PyJWK.from_dict(next(k for k in jwks.json()['keys'] if k['kid']==kid and k.get('use')=='sig')).key
 claims=jwt.decode(tokens['id_token'],key,algorithms=['RS256'],audience=client['id'],issuer=iss)
 if not secrets.compare_digest(claims.get('nonce',''),flow['nonce']):abort(400,'Invalid login nonce.')
 access=jwt.decode(tokens['access_token'],key,algorithms=['RS256'],issuer=iss,options={'verify_aud':False})
 g.session={'csrf':secrets.token_urlsafe(32),'mode':flow['mode'],'user':{'sub':claims['sub'],'name':claims.get('name',claims.get('preferred_username','')),'email':claims.get('email',''),'roles':access.get('realm_access',{}).get('roles',[])}}
 old=g.sid;g.sid=secrets.token_urlsafe(32);execute('DELETE FROM sessions WHERE id=?',(old,))
 if flow.get('jos'):return redirect(PREFIX+'/jos-cct'+('/minister' if flow.get('jos_minister') else ''))
 if flow.get('grievances'):return redirect(PREFIX+'/phase1/grievances')
 if flow.get('phase1'):return redirect(PREFIX+'/phase1')
 if flow.get('ai'):return redirect(PREFIX+'/ai?'+urlencode({'module':flow.get('ai_module','platform'),'stage':flow.get('ai_stage','')}))
 if flow.get('analytics'):return redirect(PREFIX+'/analytics?'+urlencode({'service':flow.get('dashboard_service','overview')}))
 if flow.get('simulation'):return redirect(PREFIX+'/simulation')
 for intent,service,path in [('knowledge','knowledge','/knowledge/admin'),('geography','geography','/geography'),('workspace','review','/workspace')]:
  if flow.get(intent):return redirect(PREFIX+path+'?_nsipa_records=1' if flow.get('records') else PREFIX+'/analytics?service='+service)
 return redirect(PREFIX+'/?_nsipa_records=1' if flow.get('records') else default_login_destination(flow['mode'],g.session['user']['roles']))
@app.post(PREFIX+'/logout')
def logout():g.session={};return redirect(PREFIX+'/')
@app.get(PREFIX+'/')
def home():
 p=one('SELECT * FROM profiles WHERE sub=?',(g.user.get('sub',''),));programs=rows("SELECT * FROM programs WHERE status='ACTIVE'")
 apps=rows('SELECT a.*,p.name FROM applications a JOIN programs p ON p.id=a.program WHERE a.sub=?',(g.user.get('sub',''),))
 return page('home.html',profile=p,programs=programs,applications=apps)
@app.get(PREFIX+'/profile')
def profile_form():
 require_user()
 if g.session['mode']!='beneficiary':abort(403)
 p=one('SELECT * FROM profiles WHERE sub=?',(g.user['sub'],))
 data=json.loads(p['data']) if p else {}
 with pg('master_data') as c:
  with c.cursor() as cur:cur.execute("SELECT level_value_id,level_value_mnemonic FROM g2p_geo_level_values WHERE length(level_value_id)=4 AND level_value_id LIKE 'NG%' ORDER BY level_value_mnemonic");states=cur.fetchall()
 return page('profile.html',profile=p,data=data,states=states,geocatalogue=nigeria_geography.CATALOGUE)
def clean(value,length=100):
 value=(value or '').strip()
 if len(value)>length:raise ValueError('A field exceeds its maximum length.')
 return value
@app.post(PREFIX+'/profile')
def profile_save():
 require_user()
 if g.session['mode']!='beneficiary':abort(403)
 with LOCK:
  p=one('SELECT * FROM profiles WHERE sub=?',(g.user['sub'],))
  if p and p['status']=='approved':abort(409,'This approved profile is locked. Contact the reviewer for corrections.')
  try:
   members=[]
   for i in range(8):
    given=clean(request.form.get(f'given_{i}'));family=clean(request.form.get(f'family_{i}'))
    if not given and not family:continue
    if not given or not family:raise ValueError('Each member needs a given and family name.')
    birth=datetime.date.fromisoformat(request.form.get(f'birth_{i}',''))
    if birth>datetime.date.today() or birth.year<1900:raise ValueError('Check the date of birth.')
    gender=request.form.get(f'gender_{i}')
    if gender not in ['Female','Male','Other']:raise ValueError('Select a gender for each member.')
    members.append({'given':given,'family':family,'birth_date':str(birth),'gender':gender,'ref':'IQS-REG-I-'+uuid.uuid5(uuid.NAMESPACE_URL,g.user['sub']+'/member/'+str(i)).hex[:16]})
   if not members or not request.form.get('synthetic'):raise ValueError('Add the applicant and confirm synthetic data use.')
   state=clean(request.form.get('state'));income=float(request.form.get('income','0'))
   if not 0<=income<=1000000000:raise ValueError('Income must be a non-negative monthly amount.')
   with pg('master_data') as c:
    with c.cursor() as cur:cur.execute('SELECT level_value_mnemonic FROM g2p_geo_level_values WHERE level_value_id=%s',(state,));state_row=cur.fetchone()
   if not state_row:raise ValueError('Choose a valid state or FCT.')
   data={'members':members,'state':state,'state_name':state_row[0],'community':clean(request.form.get('community')),'household_name':clean(request.form.get('household_name')),'monthly_income':income,'email':g.user.get('email',''),'synthetic':True}
   if not data['household_name']:raise ValueError('Enter a household name.')
   data['geography']=nigeria_geography.capture(request.form,data)
  except (ValueError,TypeError) as e:return page('message.html',title='Please check the form',message=str(e),back=PREFIX+'/profile'),400
  ref=members[0]['ref'];hh='IQS-REG-HH-'+uuid.uuid5(uuid.NAMESPACE_URL,g.user['sub']+'/household').hex[:16]
  execute("INSERT INTO profiles(sub,ref,household_ref,data,status,updated) VALUES(?,?,?,?,'pending_review',?) ON CONFLICT(sub) DO UPDATE SET data=excluded.data,status='pending_review',error=NULL,updated=excluded.updated",(g.user['sub'],ref,hh,json.dumps(data),stamp()));audit('registration_submitted',hh)
 return redirect(PREFIX+'/')
def sync_profile(sub):
 p=one('SELECT * FROM profiles WHERE sub=?',(sub,));d=json.loads(p['data']);members=d['members'];hh=p['household_ref'];maps={};geo=nigeria_geography.geography(d)
 geo_values={'geo_lowest_level_value_id':geo['lga_id'] or geo['state_id'],'latitude':geo['latitude'],'longitude':geo['longitude'],'geo_code_hierarchy_json':json.dumps({'region':geo['state_id'],'sub_city':geo['lga_id'],'nigeriag2p':geo})}
 individual_geo={**geo_values,'latitude':None,'longitude':None,'geo_code_hierarchy_json':json.dumps({'region':geo['state_id'],'sub_city':geo['lga_id'],'nigeriag2p':{**geo,'latitude':None,'longitude':None,'accuracy_m':None,'coordinate_source':'not_captured'}})}
 for service,database in [('registry-odoo','socialregistrydb'),('portal-backend-odoo','portalpbmsdb')]:
  o=Odoo(service,database);country=o.call('res.country','search',[[['code','=','NG']]])[0]
  hid=o.upsert('res.partner',[['ref','=',hh]],{'ref':hh,'name':d['household_name'],'is_registrant':True,'is_group':True,'country_id':country,'city':d['state_name'],'street':d['community'],'company_id':1,'comment':'IQS synthetic self-registration. Staff approved.'})
  ids=[]
  for i,m in enumerate(members):
   vals={'ref':m['ref'],'name':m['given']+' '+m['family'],'given_name':m['given'],'family_name':m['family'],'birthdate':m['birth_date'],'gender':m['gender'],'is_registrant':True,'is_group':False,'country_id':country,'company_id':1,'city':d['state_name'],'street':d['community'],'comment':'IQS synthetic registration '+hh}
   if i==0:vals['email']=d['email']
   if database=='portalpbmsdb' and i==0:
    idtype=o.upsert('g2p.id.type',[['name','=','Local UX Identity']],{'name':'Local UX Identity'})
    reg=o.call('g2p.reg.id','search_read',[[['id_type','=',idtype],['value','=',sub]]],{'fields':['partner_id']})
    if reg:pid=reg[0]['partner_id'][0];o.call('res.partner','write',[[pid],vals])
    else:pid=o.upsert('res.partner',[['ref','=',m['ref']]],vals);o.upsert('g2p.reg.id',[['value','=',sub],['id_type','=',idtype]],{'value':sub,'id_type':idtype,'partner_id':pid})
   else:pid=o.upsert('res.partner',[['ref','=',m['ref']]],vals)
   ids.append(pid)
   fields=o.call('g2p.group.membership','fields_get',[],{'attributes':['relation']});group=next(k for k,v in fields.items() if v.get('relation')=='res.partner' and 'group' in k);member=next(k for k,v in fields.items() if v.get('relation')=='res.partner' and ('individual' in k or 'member' in k))
   o.upsert('g2p.group.membership',[[group,'=',hid],[member,'=',pid]],{group:hid,member:pid})
  maps[database]={'household':hid,'individuals':ids}
 age=lambda m:(datetime.date.today()-datetime.date.fromisoformat(m['birth_date'])).days/365.2425
 adults=sum(age(m)>=18 for m in members);head=members[0];hid=str(uuid.uuid5(uuid.NAMESPACE_URL,hh))
 with pg('register') as c:
  with c.cursor() as cur:
   upsert_pg(cur,'g2p_register_households',{'internal_record_id':hid,'functional_record_id':hh,'record_name':d['household_name'],'created_by':'iqs-registration','created_at':stamp(),'last_approved_at':stamp(),'last_approved_by':'iqs-staff-review','record_status':'ACTIVE','search_text':d['household_name']+' '+hh,'household_head_internal_record_id':str(uuid.uuid5(uuid.NAMESPACE_URL,head['ref'])),'household_head_name':head['given']+' '+head['family'],'size_total':len(members),'size_adults':adults,'country_code':'NGA',**geo_values},'internal_record_id')
   for m in members:
    name=m['given']+' '+m['family'];upsert_pg(cur,'g2p_register_individuals',{'internal_record_id':str(uuid.uuid5(uuid.NAMESPACE_URL,m['ref'])),'functional_record_id':m['ref'],'link_internal_record_id':hid,'record_name':name,'created_by':'iqs-registration','created_at':stamp(),'last_approved_at':stamp(),'last_approved_by':'iqs-staff-review','record_status':'ACTIVE','search_text':name+' '+m['ref'],'first_name':m['given'],'last_name':m['family'],'given_name':m['given'],'full_name':name,'gender':m['gender'],'birth_date':m['birth_date'],'country_code':'NGA',**individual_geo,'address_line_1':d['community']},'internal_record_id')
 pb=Odoo('pbms-odoo','pbmsdb');rid=pb.upsert('g2p.household.registry',[['link_registry_id','=',hh]],{'link_registry_id':hh,'name':d['household_name'],'gender':head['gender'].lower(),'size_total':len(members),'size_adults':adults,'size_children':len(members)-adults,'annual_income':d['monthly_income']*12,'large_area_code':d['state_name'],'small_area_code':d['community']})
 maps['pbms_household']=rid
 execute("UPDATE profiles SET sync_status='complete',mapping=?,portal_partner=?,error=NULL WHERE sub=?",(json.dumps(maps),maps['portalpbmsdb']['individuals'][0],sub))
def create_program(mnemonic,name,amount,max_income,min_members):
 pb=Odoo('pbms-odoo','pbmsdb');po=Odoo('portal-backend-odoo','portalpbmsdb')
 benefit=pb.upsert('g2p.benefit.codes',[['benefit_mnemonic','=',mnemonic]],{'benefit_mnemonic':mnemonic,'benefit_type':'CASH_DIGITAL','benefit_description':name+' — synthetic integration, no payment execution','measurement_unit':'NGN'})
 pid=pb.upsert('g2p.program.definition',[['program_mnemonic','=',mnemonic]],{'program_mnemonic':mnemonic,'description':name+' — IQS Integrated Sandbox','target_registry':'household','program_status':'ACTIVE','enrollment_frequency':'OnDemand','disbursement_frequency':'OnDemand','beneficiary_list':'latest_always','auto_approve_enrolment':False,'auto_approve_disbursement':False})
 pb.upsert('g2p.program.benefit.codes',[['program_id','=',pid],['benefit_code_id','=',benefit]],{'program_id':pid,'benefit_code_id':benefit,'max_quantity':amount})
 today=str(datetime.date.today());end=str(datetime.date.today()+datetime.timedelta(days=365))
 cycle=pb.upsert('g2p.enrollment.cycle',[['program_id','=',pid],['cycle_number','=',1]],{'program_id':pid,'cycle_number':1,'enrollment_cycle_id':mnemonic+'-C01','enrollment_start_date':today,'enrollment_end_date':end,'disbursement_start_date':today,'disbursement_end_date':end,'approved_for_enrollment':True})
 pb.upsert('g2p.entitlement.rule.definition',[['mnemonic','=',mnemonic+'-ENT']],{'mnemonic':mnemonic+'-ENT','program_id':pid,'target_registry':'household','benefit_code_id':benefit,'quantity':amount,'pbms_domain':"[('link_registry_id','like','IQS-REG-HH-%')]"})
 formids=po.call('formio.builder','search',[[['title','=','IQS Synthetic Support Application'],['state','=','CURRENT']]])
 if not formids:formids=po.call('formio.builder','search',[[['name','=','nigeria_lab_application']]])
 if not formids:raise RuntimeError('The portal requires a published application form before programme creation.')
 vals={'name':name+' — IQS Integrated Sandbox','description':'Synthetic household programme connected to PBMS. Register at '+BASE+PREFIX+'/','active':True}
 if formids:vals['portal_form_builder_id']=formids[0]
 portal_id=po.upsert('g2p.program',[['name','=',vals['name']]],vals)
 execute('INSERT INTO programs(id,mnemonic,name,amount,max_income,min_members,portal_id,cycle_id,benefit_id) VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,amount=excluded.amount,max_income=excluded.max_income,min_members=excluded.min_members',(pid,mnemonic,name,amount,max_income,min_members,portal_id,cycle,benefit))
 update_rules(pid)
 return pid
def update_rules(pid):
 p=one('SELECT * FROM programs WHERE id=?',(pid,));refs=[r['household_ref'] for r in rows("SELECT p.household_ref FROM applications a JOIN profiles p ON p.sub=a.sub WHERE a.program=? AND a.status IN ('checking_eligibility','eligible','enrolled') AND p.status='approved' AND p.sync_status='complete'",(pid,))]
 # This installed Odoo domain converter misquotes IN tuples; equality/OR works reliably.
 matches=[('link_registry_id','=',ref) for ref in refs] or [('link_registry_id','=','IQS-NO-APPROVED-APPLICATION')]
 domain=repr(['|']*(len(matches)-1)+matches+[('annual_income','<=',p['max_income']*12),('size_total','>=',p['min_members'])]);pb=Odoo('pbms-odoo','pbmsdb')
 pb.upsert('g2p.eligibility.rule.definition',[['mnemonic','=',p['mnemonic']+'-ELIG']],{'mnemonic':p['mnemonic']+'-ELIG','program_id':pid,'target_registry':'household','pbms_domain':domain})
def link_portal_application(a):
 p=one('SELECT * FROM profiles WHERE sub=?',(a['sub'],));program=one('SELECT * FROM programs WHERE id=?',(a['program'],));po=Odoo('portal-backend-odoo','portalpbmsdb')
 membership=po.upsert('g2p.program_membership',[['partner_id','=',p['portal_partner']],['program_id','=',program['portal_id']]],{'partner_id':p['portal_partner'],'program_id':program['portal_id'],'company_id':1,'state':'draft'})
 info=po.upsert('g2p.program.registrant_info',[['program_membership_id','=',membership]],{'registrant_id':p['portal_partner'],'program_id':program['portal_id'],'program_membership_id':membership,'state':'inprogress','application_id':str(92000000000+a['id']),'program_registrant_info':{'contactName':json.loads(p['data'])['members'][0]['given'],'householdRef':p['household_ref'],'supportRequest':'IQS synthetic integrated programme application','demoConsent':True}})
 execute('UPDATE applications SET portal_info=?,portal_membership=?,error=NULL WHERE id=?',(info,membership,a['id']))
def start_eligibility(a):
 update_rules(a['program']);program=one('SELECT * FROM programs WHERE id=?',(a['program'],));pb=Odoo('pbms-odoo','pbmsdb')
 household=one('SELECT household_ref FROM profiles WHERE sub=?',(a['sub'],))['household_ref']
 listing=pb.upsert('g2p.beneficiary.list',[['mnemonic','=',f'IQS-REG-APP-{a["id"]}']],{'mnemonic':f'IQS-REG-APP-{a["id"]}','enrollment_cycle_id':program['cycle_id'],'iqs_household_ref':household,'brief':f'Staff-reviewed synthetic application {a["id"]}; no payment execution.','eligibility_process_status':'pending'})
 execute('UPDATE applications SET pbms_list=? WHERE id=?',(listing,a['id']))
@app.post(PREFIX+'/apply/<int:pid>')
def apply_program(pid):
 require_user()
 p=one('SELECT * FROM profiles WHERE sub=?',(g.user['sub'],));program=one("SELECT * FROM programs WHERE id=? AND status='ACTIVE'",(pid,))
 if g.session['mode']!='beneficiary' or not p or p['status']!='approved' or p['sync_status']!='complete' or not program:abort(409,'An approved, synchronized household is required.')
 with LOCK:
  execute('INSERT OR IGNORE INTO applications(sub,program,created) VALUES(?,?,?)',(g.user['sub'],pid,stamp()));a=one('SELECT * FROM applications WHERE sub=? AND program=?',(g.user['sub'],pid))
  if not a['portal_info']:link_portal_application(a)
  audit('programme_application',a['id'])
 return redirect(PREFIX+'/')
@app.get(PREFIX+'/staff')
def staff_home():
 require_staff();return page('staff.html',profiles=rows('SELECT * FROM profiles ORDER BY updated DESC'),applications=rows('SELECT a.*,p.name,r.household_ref FROM applications a JOIN programs p ON p.id=a.program JOIN profiles r ON r.sub=a.sub ORDER BY a.id DESC'),programs=rows('SELECT * FROM programs'),events=rows('SELECT * FROM audit ORDER BY id DESC LIMIT 20'))
@app.get(PREFIX+'/staff/profile/<sub>')
def staff_profile(sub):
 require_staff();p=one('SELECT * FROM profiles WHERE sub=?',(sub,))
 if not p:abort(404)
 return page('review.html',profile=p,data=json.loads(p['data']))
@app.post(PREFIX+'/staff/profile/<sub>/<action>')
def staff_profile_decision(sub,action):
 require_staff()
 if action not in ['approve','reject','retry']:abort(404)
 with LOCK:
  p=one('SELECT * FROM profiles WHERE sub=?',(sub,))
  if not p:abort(404)
  if action=='reject':
   if p['status']!='pending_review':abort(409,'This registration is no longer awaiting review.')
   if is_maker(p,g.user['sub']):abort(403,'A different reviewer must decide a record you created or corrected.')
   if p['status']=='approved':abort(409,'Approved records cannot be rejected retrospectively.')
   reason=clean(request.form.get('reason'),500)
   if len(reason)<10:abort(400,'Give a clear correction reason of at least 10 characters.')
   execute("UPDATE profiles SET status='rejected',error=?,updated=? WHERE sub=?",(reason,stamp(),sub))
  else:
   if action=='retry' and p['status']!='approved':abort(409)
   if action=='approve':
    if p['status']!='pending_review':abort(409,'This record is no longer awaiting review.')
    if is_maker(p,g.user['sub']):abort(403,'A different reviewer must decide a record you created or corrected.')
   execute("UPDATE profiles SET status='approved',sync_status='pending',error=NULL,updated=? WHERE sub=?",(stamp(),sub))
   try:sync_profile(sub)
   except Exception:logging.exception('Profile synchronization failed');execute("UPDATE profiles SET sync_status='pending',error='A backend is unavailable. The saved registration will retry.' WHERE sub=?",(sub,))
  audit('registration_'+action,sub)
 return redirect(PREFIX+'/staff')
@app.post(PREFIX+'/staff/program')
def staff_program_create():
 require_staff()
 try:
  name=clean(request.form.get('name'));suffix=clean(request.form.get('mnemonic')).upper();amount=float(request.form.get('amount'));income=float(request.form.get('max_income'));minimum=int(request.form.get('min_members'))
  if not name or not suffix.replace('_','').isalnum() or len(suffix)>30 or not 0<amount<=1000000 or not 0<=income<=1000000000 or not 1<=minimum<=8:raise ValueError('Check programme name, mnemonic and numeric values.')
  mnemonic='IQS_INTEGRATED_'+suffix
  if one('SELECT * FROM programs WHERE mnemonic=?',(mnemonic,)):raise ValueError('This mnemonic already exists. Choose a new one.')
  with LOCK:pid=create_program(mnemonic,name,amount,income,minimum);audit('programme_created',pid)
 except ValueError as e:return page('message.html',title='Check programme details',message=str(e),back=PREFIX+'/staff'),400
 return redirect(PREFIX+'/staff')
@app.post(PREFIX+'/staff/application/<int:aid>/<action>')
def staff_application_decision(aid,action):
 require_staff()
 with LOCK:
  a=one('SELECT * FROM applications WHERE id=?',(aid,))
  if not a:abort(404)
  pb=Odoo('pbms-odoo','pbmsdb');po=Odoo('portal-backend-odoo','portalpbmsdb')
  if action=='check' and a['status']=='pending_review':
   execute("UPDATE applications SET status='checking_eligibility',error=NULL WHERE id=?",(aid,));start_eligibility(a)
  elif action=='enroll' and a['status']=='eligible':
   listing=pb.call('g2p.beneficiary.list','read',[[a['pbms_list']]],{'fields':['eligibility_process_status','number_of_registrants']})[0]
   if listing['eligibility_process_status']!='complete':abort(409,'Eligibility processing has not completed.')
   pb.call('g2p.beneficiary.list','write',[[a['pbms_list']],{'list_workflow_status':'approved_final_enrolment','approval_date':str(datetime.date.today())}])
   po.call('g2p.program_membership','write',[[a['portal_membership']],{'state':'enrolled'}]);po.call('g2p.program.registrant_info','write',[[a['portal_info']],{'state':'active'}]);execute("UPDATE applications SET status='enrolled',error=NULL WHERE id=?",(aid,))
  elif action=='reject' and a['status'] in ['pending_review','eligible']:
   po.call('g2p.program_membership','write',[[a['portal_membership']],{'state':'not_eligible'}]);po.call('g2p.program.registrant_info','write',[[a['portal_info']],{'state':'rejected'}]);execute("UPDATE applications SET status='rejected' WHERE id=?",(aid,));update_rules(a['program'])
  else:abort(409,'This action is not available for the current status.')
  audit('application_'+action,aid)
 return redirect(PREFIX+'/staff')
def reconcile():
 with LOCK:
  execute('DELETE FROM sessions WHERE expires<?',(int(time.time()),))
  for p in rows("SELECT * FROM profiles WHERE status='approved' AND sync_status!='complete'"):
   try:sync_profile(p['sub'])
   except Exception:logging.exception('Retry synchronization failed')
  # Discover applications submitted in the existing beneficiary portal.
  po=Odoo('portal-backend-odoo','portalpbmsdb')
  for program in rows('SELECT * FROM programs'):
   apps=po.call('g2p.program.registrant_info','search_read',[[['program_id','=',program['portal_id']]]],{'fields':['registrant_id','program_membership_id','state']})
   for item in apps:
    partner=item['registrant_id'][0] if isinstance(item['registrant_id'],list) else item['registrant_id'];p=one("SELECT * FROM profiles WHERE portal_partner=? AND status='approved' AND sync_status='complete'",(partner,))
    if p:
     execute('INSERT OR IGNORE INTO applications(sub,program,portal_info,portal_membership,created) VALUES(?,?,?,?,?)',(p['sub'],program['id'],item['id'],item['program_membership_id'][0],stamp()))
  for a in rows("SELECT * FROM applications WHERE status='checking_eligibility' AND pbms_list IS NULL"):start_eligibility(a)
  pending=rows("SELECT * FROM applications WHERE status='checking_eligibility' AND pbms_list IS NOT NULL")
  if pending:
   pb=Odoo('pbms-odoo','pbmsdb')
   for a in pending:
    listing=pb.call('g2p.beneficiary.list','read',[[a['pbms_list']]],{'fields':['eligibility_process_status','eligibility_latest_error_code','beneficiary_list_id']})[0]
    if listing['eligibility_latest_error_code']:execute('UPDATE applications SET error=? WHERE id=?',('PBMS processing reported an error; inspect its job details.',a['id']))
    if listing['eligibility_process_status']=='complete':
     p=one('SELECT * FROM profiles WHERE sub=?',(a['sub'],))
     with pg('bgtaskdb','pbms-postgresql') as c:
      with c.cursor() as cur:
       cur.execute('SELECT registrant_details FROM beneficiary_list_details WHERE beneficiary_list_id=%s',(listing['beneficiary_list_id'],));details=cur.fetchall()
     eligible=any(any(str(item.get('registrant_id'))==p['household_ref'] for item in (r[0] if isinstance(r[0],list) else json.loads(r[0]))) for r in details)
     execute('UPDATE applications SET status=?,error=NULL WHERE id=?',('eligible' if eligible else 'not_eligible',a['id']))
     if not eligible:
      po.call('g2p.program_membership','write',[[a['portal_membership']],{'state':'not_eligible'}]);po.call('g2p.program.registrant_info','write',[[a['portal_info']],{'state':'rejected'}])
  for a in rows('SELECT * FROM applications WHERE portal_info IS NULL'):
   try:link_portal_application(a)
   except Exception:logging.exception('Application sync failed')
@app.errorhandler(Exception)
def error(e):
 from werkzeug.exceptions import HTTPException
 if isinstance(e,HTTPException):
  if request.path.startswith(PREFIX+'/api/'):return {'error':e.description},e.code
  return page('message.html',title='Action needs attention',message=e.description,back=PREFIX+'/'),e.code
 logging.exception('Integration request failed')
 if request.path.startswith(PREFIX+'/api/'):return {'error':'Service temporarily unavailable. Refresh before trying again.'},503
 return page('message.html',title='Service temporarily unavailable',message='Your saved records are retained. Try again shortly; staff can inspect integration logs.',back=PREFIX+'/'),503
import registration_workspaces
registration_workspaces.install(os.sys.modules[__name__])
nigeria_geography.install(os.sys.modules[__name__])
knowledge_management.install(os.sys.modules[__name__])
local_ai.install(os.sys.modules[__name__])
import platform_analytics
platform_analytics.install(os.sys.modules[__name__])
import partner_simulation
partner_simulation.install(os.sys.modules[__name__])
import phase1_sandbox
phase1_sandbox.install(os.sys.modules[__name__])
import jos_connected
jos_connected.install(os.sys.modules[__name__])
if __name__=='__main__':
 if '--reconcile' in os.sys.argv:reconcile()
 else:app.run(host='127.0.0.1',port=18081)
