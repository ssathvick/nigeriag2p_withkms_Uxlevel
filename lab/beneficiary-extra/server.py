"""Beneficiary UI adapter. Existing intake, grievances, CMS and signed mapper remain authoritative."""
import base64, datetime as dt, fcntl, hashlib, hmac, json, os, re, secrets, sqlite3, time, uuid
from pathlib import Path
import jwt, requests
from flask import Flask, abort, g, request
from werkzeug.exceptions import HTTPException

ROOT=Path(os.getenv('BENEFICIARY_DATA_ROOT','/opt/openg2p-lab/registration'))
CONFIG=json.loads(Path(os.getenv('BENEFICIARY_CONFIG','/opt/openg2p-lab/beneficiary-extra/config.json')).read_text())
ISSUER='https://g2p-keycloak.wverve.in/realms/beneficiary'
HOSTS={'g2p-beneficiary.wverve.in','beneficiary.nigeriag2p.com'}
app=Flask(__name__);app.config['MAX_CONTENT_LENGTH']=16000
keys=jwt.PyJWKClient(CONFIG['jwks'],cache_keys=True,lifespan=300)
def db(phase=False):
 c=sqlite3.connect(ROOT/('phase1-sandbox.sqlite' if phase else 'intake.sqlite'),timeout=30);c.row_factory=sqlite3.Row;return c
def rows(sql,args=(),phase=False):
 with db(phase) as c:return [dict(x) for x in c.execute(sql,args)]
with db() as c:c.execute('CREATE TABLE IF NOT EXISTS beneficiary_notification_reads(sub TEXT NOT NULL,id TEXT NOT NULL,read_at TEXT NOT NULL,PRIMARY KEY(sub,id))')
def now():return dt.datetime.now(dt.timezone.utc).isoformat(timespec='milliseconds').replace('+00:00','Z')
def own():
 p=rows('SELECT household_ref,data,status,sync_status,updated FROM profiles WHERE sub=?',(g.sub,))
 if not p:return None
 p=p[0];p['data']=json.loads(p['data']);return p
def csrf():return hmac.new(CONFIG['secret'].encode(),g.token.encode(),hashlib.sha256).hexdigest()
@app.before_request
def auth():
 if request.path=='/health':return
 if request.host.split(':')[0] not in HOSTS:abort(400,'Unknown service host.')
 g.token=request.cookies.get('X-Access-Token','')
 try:
  claims=jwt.decode(g.token,keys.get_signing_key_from_jwt(g.token).key,algorithms=['RS256'],issuer=ISSUER,audience='account',options={'require':['exp','iat','sub','iss','aud']})
  if claims.get('azp')!='nigeria-beneficiary-portal':raise ValueError()
  g.sub=claims['sub'];g.claims=claims
 except Exception:abort(401,'Your session has expired. Sign in to the NSIPA beneficiary portal again.')
 if request.method!='GET':
  if request.headers.get('Origin') not in {'https://'+x for x in HOSTS}:abort(403,'Reload this screen before submitting.')
  # Nginx translates canonical Host, but preserves the browser Origin.
  if not hmac.compare_digest(request.headers.get('X-CSRF-Token',''),csrf()):abort(403,'Reload this screen before submitting.')
  if not request.is_json:abort(415,'JSON is required.')
  if not isinstance(request.get_json(),dict):abort(400,'A JSON object is required.')
@app.after_request
def headers(r):
 r.headers['Cache-Control']='no-store';r.headers['X-Content-Type-Options']='nosniff';return r
@app.errorhandler(HTTPException)
def error(e):return {'error':e.description},e.code
@app.errorhandler(Exception)
def failure(e):
 app.logger.error('Beneficiary service failure: %s',type(e).__name__)
 return {'error':'The service could not complete this request. Refresh to check the recorded result before retrying.'},502
@app.get('/health')
def health():return {'status':'ok'}
@app.get('/beneficiary-api/session')
def session():return {'name':g.claims.get('name',g.claims.get('preferred_username','Beneficiary')),'csrf':csrf()}
@app.get('/beneficiary-api/registries')
def registries():return {'profile':own()}
def cases():return rows('SELECT id,reason,channel,status,version,created,response_due,resolution_due,responded,resolved FROM grievances WHERE actor=? ORDER BY created DESC LIMIT 200',(g.sub,),True)
@app.get('/beneficiary-api/complaints')
def complaints():return {'items':cases(),'canSubmit':bool(own())}
@app.post('/beneficiary-api/complaints')
def create_complaint():
 data=request.get_json();p=own()
 if not p:abort(409,'Register your household before submitting a complaint.')
 if set(data)-{'reason','request_id'}:abort(400,'Unsupported complaint fields.')
 if data.get('reason') not in ['payment_delay','account_issue','registration_correction','service_quality']:abort(400,'Choose a supported complaint reason.')
 try:key=str(uuid.UUID(data.get('request_id','')))
 except (ValueError,TypeError,AttributeError):abort(400,'A valid submission identifier is required.')
 # A short-lived internal session bridges the verified native beneficiary identity.
 # The existing endpoint still owns permissions, validation, idempotency and audit.
 sid=secrets.token_urlsafe(32);token=secrets.token_urlsafe(32)
 bridge={'csrf':token,'mode':'beneficiary','user':{'sub':g.sub,'name':g.claims.get('name',''),'roles':[]}}
 with db() as c:c.execute('INSERT INTO sessions VALUES(?,?,?)',(sid,json.dumps(bridge),int(time.time())+60))
 try:
  r=requests.post('http://127.0.0.1:18081/registration/phase1/grievances',headers={'Host':'g2p.wverve.in','Cookie':'IQS-INTAKE='+sid},data={'csrf':token,'request_id':key,'reason':data['reason'],'channel':'web','household':p['household_ref']},allow_redirects=False,timeout=30)
  if r.status_code not in (302,303):abort(r.status_code if 400<=r.status_code<500 else 502,'The complaint was not accepted. Refresh and check your cases before retrying.')
 finally:
  with db() as c:c.execute('DELETE FROM sessions WHERE id=?',(sid,))
 return {'items':cases(),'canSubmit':True},201
@app.get('/beneficiary-api/news')
def news():
 lang=request.args.get('lang','en')
 if lang not in ('en','ha','yo','ig'):abort(400,'Unsupported language.')
 items=[]
 for r in rows("SELECT id,published,published_version,updated FROM cms_entries WHERE kind='news' AND published IS NOT NULL AND status!='archived' ORDER BY updated DESC",phase=True):
  text=json.loads(r.pop('published')).get(lang)
  if text:items.append({**r,**{k:re.sub(r'Nigeria\s*G2P','NSIPA',v,flags=re.I) for k,v in text.items()}})
 return {'items':items}
def inbox():
 p=own();items=[]
 if p:
  items.extend({'id':'registration-'+str(r['id']),'title':'Payment account' if r['action'].startswith('payment_account_') else 'Household registration','body':r['action'].replace('_',' ').capitalize()+('. This records an account mapping change, not a payment.' if r['action'].startswith('payment_account_') else '. Current status: '+p['status'].replace('_',' ')+'.'),'at':r['at']} for r in rows('SELECT id,action,at FROM audit WHERE reference IN (?,?) ORDER BY id DESC LIMIT 100',(g.sub,p['household_ref'])))
 for c in cases():
  items.extend({'id':'complaint-'+str(e['id']),'title':'Complaint '+c['id'],'body':e['action'].replace('_',' ').capitalize()+'. Current status: '+c['status']+'.','at':e['at']} for e in rows('SELECT id,action,at FROM events WHERE reference=? ORDER BY id DESC',(c['id'],),True))
 for a in rows('SELECT a.id,a.status,a.created,p.name FROM applications a JOIN programs p ON p.id=a.program WHERE a.sub=?',(g.sub,)):
  items.append({'id':'application-'+str(a['id'])+'-'+a['status'],'title':a['name'],'body':'Application status: '+a['status'].replace('_',' ')+'. Approval does not confirm payment.','at':a['created']})
 read={r['id'] for r in rows('SELECT id FROM beneficiary_notification_reads WHERE sub=?',(g.sub,))}
 return [{**r,'read':r['id'] in read} for r in sorted(items,key=lambda r:r['at'],reverse=True)[:200]]
@app.get('/beneficiary-api/notifications')
def notifications():return {'items':inbox()}
@app.post('/beneficiary-api/notifications/read')
def mark_read():
 data=request.get_json();ids=data.get('ids')
 if set(data)!={'ids'} or not isinstance(ids,list) or not ids or len(ids)>200 or not all(isinstance(i,str) for i in ids):abort(400,'Choose notifications to mark as read.')
 if not set(ids).issubset({r['id'] for r in inbox()}):abort(404,'Notification not found.')
 with db() as c:c.executemany('INSERT OR IGNORE INTO beneficiary_notification_reads VALUES(?,?,?)',[(g.sub,i,now()) for i in ids])
 return {'items':inbox()}
def mapper(action,identity,fa=None,name=None):
 stamp=now();rid=str(uuid.uuid4());entry={'reference_id':rid,'timestamp':stamp,'id':identity,'locale':'en'}
 if action=='resolve':entry.update(fa='',scope='details')
 elif action!='unlink':entry.update(fa=fa,name=name)
 payload={'request_header':{'sender_app_mnemonic':'g2p_bridge','sender_app_url':'https://bridge.openg2p.localhost','request_id':rid,'request_timestamp':stamp},'request_body':{'request_payload':{'transaction_id':rid,action+'_request':[entry]}}}
 encoded=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
 signed=requests.post(CONFIG['keymanager']+'/v1/keymanager/jwtSign',json={'id':'nsipa-beneficiary','version':'1.0','requesttime':stamp,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':encoded,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=25)
 signed.raise_for_status();signature=signed.json()['response']['jwtSignedData']
 r=requests.post(CONFIG['mapper']+'/mapper/'+action,json=payload,headers={'Signature':signature},timeout=30);r.raise_for_status();d=r.json()
 if d.get('response_header',{}).get('response_status')!='SUCCESS':abort(502,'The account service could not complete the request. Refresh before retrying.')
 result=d['response_body']['response_payload'][action+'_response'][0]
 if result['status']!='succ':abort(409,'The account service rejected this change. Refresh your account details before retrying.')
 return result
def account(p):
 fa=mapper('resolve',p['household_ref']).get('fa') if p and p['status']=='approved' and p['sync_status']=='complete' else None
 return {'account':fa,'version':hashlib.sha256(json.dumps(fa,sort_keys=True).encode()).hexdigest(),'eligible':bool(p and p['status']=='approved' and p['sync_status']=='complete')}
@app.get('/beneficiary-api/accounts')
def accounts():return account(own())
@app.post('/beneficiary-api/accounts')
def change_account():
 data=request.get_json();p=own()
 if not p or p['status']!='approved' or p['sync_status']!='complete':abort(409,'Your household must be approved and synchronised before linking an account.')
 if set(data)-{'action','account_number','version'}:abort(400,'Unsupported account fields.')
 action=data.get('action')
 if action not in ('link','update','unlink'):abort(400,'Choose a supported action.')
 number=data.get('account_number','')
 if action!='unlink' and (not isinstance(number,str) or not re.fullmatch(r'LAB-[A-Za-z0-9-]{4,32}',number)):abort(400,'Use a fictional simulator account beginning LAB- followed by 4–32 letters, digits or hyphens.')
 with open(ROOT/'beneficiary-mapper.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);current=account(p)
  if data.get('version')!=current['version']:abort(409,'This account changed. Refresh before submitting again.')
  if (action=='link' and current['account']) or (action!='link' and not current['account']):abort(409,'Refresh to use the current account action.')
  fa={'strategy_id':5,'fa_type':'BANK','bank_name':'Example Bank Simulator','bank_code':'EXAMPLE_BANK','branch_name':'Local Test Branch','branch_code':'LAB','account_number':number}
  mapper(action,p['household_ref'],fa,p['data'].get('household_name','NSIPA household'))
  with db() as c:c.execute('INSERT INTO audit(actor,action,reference,at) VALUES(?,?,?,?)',(g.sub,'payment_account_'+action,p['household_ref'],now()))
  return account(p)


