"""Versioned multilingual plain-text publishing with independent review."""
import json
import uuid
from flask import Blueprint, abort, g, request, redirect
LOCALES=('en','ha','yo','ig')
# Language strings are draft translations for review by NSIPA language owners.
LABELS={
'en':['NigeriaG2P demonstration portal','Fictional sandbox only. No real payment or eligibility decision.','Programmes','News','Guidance and policies','Service locations','Public demonstration data','Household registration','Knowledge library','My grievance cases','Staff workspace','Language','Skip to content','Version','Find a service location','Find locations','No matching locations','These are demonstration examples, not official NSIPA policy or operational service centres.','Published entries','Demonstration zones'],
'ha':['Shafin gwaji na NigeriaG2P','Gwaji ne kawai. Babu biyan kuɗi na gaske ko yanke shawarar cancanta.','Shirye-shirye','Labarai','Jagora da manufofi','Wuraren hidima','Bayanan gwaji na jama’a','Rajistar iyali','Ɗakin bayanai','Korafe-korafena','Wurin aikin ma’aikata','Harshe','Tsallaka zuwa abun ciki','Siga','Nemo wurin hidima','Nemo wurare','Babu wurin da ya dace','Waɗannan misalan gwaji ne, ba manufofin NSIPA na hukuma ko cibiyoyin hidima na aiki ba.','Bayanan da aka wallafa','Yankunan gwaji'],
'yo':['Ojú ìwé ìdánwò NigeriaG2P','Ìdánwò nìkan. Kò sí ìsanwó gidi tàbí ìpinnu ẹ̀tọ́ sí àǹfààní.','Àwọn ètò','Ìròyìn','Ìtọ́sọ́nà àti àwọn ìlànà','Àwọn ibi iṣẹ́','Dátà ìdánwò fún gbogbo ènìyàn','Ìforúkọsílẹ̀ ìdílé','Ilé ìkàwé ìmọ̀','Àwọn ẹ̀dùn ọkàn mi','Ibùdó iṣẹ́ òṣìṣẹ́','Èdè','Lọ sí àkóónú','Ẹ̀dà','Wa ibi iṣẹ́','Wa àwọn ibi','Kò sí ibi tí ó bá àwárí mu','Àwọn wọ̀nyí jẹ́ àpẹẹrẹ ìdánwò, wọn kì í ṣe ìlànà NSIPA tàbí ibi iṣẹ́ gidi.','Àwọn àkọsílẹ̀ tí a tẹ̀ jáde','Àwọn agbègbè ìdánwò'],
'ig':['Ọnụ ụzọ nnwale NigeriaG2P','Naanị nnwale. Enweghị ịkwụ ụgwọ n’ezie ma ọ bụ mkpebi ntozu.','Mmemme','Akụkọ','Nduzi na iwu','Ebe ọrụ','Data nnwale ọha','Ndebanye ezinụlọ','Ọba ihe ọmụma','Mkpesa m','Ebe ọrụ ndị ọrụ','Asụsụ','Gaa na ọdịnaya','Ụdị','Chọta ebe ọrụ','Chọta ebe','Enweghị ebe dabara','Ndị a bụ ihe atụ nnwale, ọ bụghị iwu NSIPA ma ọ bụ ebe ọrụ na-arụ ọrụ n’ezie.','Ihe e bipụtara','Mpaghara nnwale']}
NAMES={
'en':['Demonstration household support','Sandbox testing is available','Use fictional data'],
'ha':['Tallafin iyali na gwaji','Gwajin tsarin yana samuwa','Yi amfani da bayanan gwaji'],
'yo':['Ìrànlọ́wọ́ ìdílé fún ìdánwò','Ìdánwò ètò ti wà','Lo dátà ìdánwò'],
'ig':['Nkwado ezinụlọ nnwale','Nnwale usoro dị','Jiri data nnwale']}
BODIES={
'en':['Register a fictional household, submit it for independent review, then apply to a demonstration programme. Approval of registration does not establish benefit entitlement.','Staff can test grievances, fictional agent certification and device delivery synchronisation. Use only supplied fictional data.','Do not enter real NIN, BVN, biometric records or bank account details. Real integrations and formal platform acceptance require separate validation.'],
'ha':['Yi rajistar iyali na gwaji, aika shi don tantancewa mai zaman kanta, sannan nemi shiga shirin gwaji. Amincewa da rajista ba ta tabbatar da cancantar tallafi ba.','Ma’aikata za su iya gwada korafe-korafe, takardar shaidar wakilin gwaji da daidaita bayanan isarwa. A yi amfani da bayanan gwaji kawai.','Kada a shigar da NIN, BVN, bayanan halittar mutum ko asusun banki na gaske. Haɗin tsarin na gaske da amincewar hukuma suna buƙatar tantancewa daban.'],
'yo':['Forúkọsílẹ̀ ìdílé ìdánwò, fi sílẹ̀ fún àyẹ̀wò olómìnira, lẹ́yìn náà béèrè fún ètò ìdánwò. Ìfọwọ́sí ìforúkọsílẹ̀ kò túmọ̀ sí ẹ̀tọ́ sí àǹfààní.','Àwọn òṣìṣẹ́ lè dán ẹ̀dùn ọkàn, ìjẹ́rìísí aṣojú ìdánwò àti ìṣiṣẹ́pọ̀ dátà ìfijiṣẹ́ wò. Lo dátà ìdánwò nìkan.','Má ṣe fi NIN, BVN, dátà ìdánimọ̀ ara tàbí àlàyé àkọọ́lẹ̀ banki gidi sínú ìdánwò yìí. Ìsopọ̀ gidi àti ìfọwọ́sí ètò nílò àyẹ̀wò ọ̀tọ̀.'],
'ig':['Debanye ezinụlọ nnwale, ziga ya maka nyocha nọọrọ onwe ya, wee tinye akwụkwọ maka mmemme nnwale. Nkwado ndebanye anaghị egosi ntozu uru.','Ndị ọrụ nwere ike ịnwale mkpesa, asambodo onye nnọchi anya nnwale na mmekọrịta data nnyefe. Jiri naanị data nnwale e nyere.','Etinyela ezigbo NIN, BVN, data njirimara ahụ ma ọ bụ nkọwa akaụntụ ụlọ akụ. Njikọ n’ezie na nkwado usoro chọrọ nyocha dị iche.']}

def install(r,db,locations):
 bp=Blueprint('phase1_cms',__name__)
 with db() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS cms_entries(id TEXT PRIMARY KEY,kind TEXT NOT NULL,draft TEXT NOT NULL,version INTEGER NOT NULL,status TEXT NOT NULL,author TEXT NOT NULL,reviewer TEXT,published TEXT,published_version INTEGER,updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cms_history(id INTEGER PRIMARY KEY,entry TEXT NOT NULL,version INTEGER NOT NULL,action TEXT NOT NULL,actor TEXT NOT NULL,at TEXT NOT NULL,content TEXT NOT NULL);''')
  for i,kind in enumerate(('programme','news','policy')):
   payload=json.dumps({lang:{'title':NAMES[lang][i],'body':BODIES[lang][i]} for lang in LOCALES});eid='DEMO-CMS-'+kind
   cur=c.execute("INSERT OR IGNORE INTO cms_entries VALUES(?,?,?,1,'published','system:demo-seed','system:demo-seed',?,1,?)",(eid,kind,payload,payload,r.stamp()))
   if cur.rowcount:c.execute('INSERT INTO cms_history(entry,version,action,actor,at,content) VALUES(?,1,?,?,?,?)',(eid,'seed','system:demo-seed',r.stamp(),payload))
 def require(action):
  r.require_user();allowed={'view':{'iqs-registration-officer','iqs-verification-officer','iqs-programme-supervisor','iqs-intake-reviewer'},'edit':{'iqs-registration-officer','iqs-programme-supervisor','iqs-intake-reviewer'},'review':{'iqs-verification-officer','iqs-intake-reviewer'},'publish':{'iqs-programme-supervisor','iqs-intake-reviewer'}}
  if g.session.get('mode')!='staff' or not set(g.user.get('roles',[])).intersection(allowed[action]):abort(403,'Your account cannot perform this publishing action.')
 def permissions():
  roles=set(g.user.get('roles',[]));staff=g.session.get('mode')=='staff'
  return {action:staff and bool(roles.intersection(values)) for action,values in {'edit':{'iqs-registration-officer','iqs-programme-supervisor','iqs-intake-reviewer'},'review':{'iqs-verification-officer','iqs-intake-reviewer'},'publish':{'iqs-programme-supervisor','iqs-intake-reviewer'}}.items()}
 def history(c,row,action):c.execute('INSERT INTO cms_history(entry,version,action,actor,at,content) VALUES(?,?,?,?,?,?)',(row['id'],row['version'],action,g.user['sub'],r.stamp(),row['draft']))
 def live(lang):
  with db() as c:rows=c.execute("SELECT * FROM cms_entries WHERE published IS NOT NULL AND status!='archived' ORDER BY kind,id").fetchall()
  return [{'id':x['id'],'kind':x['kind'],'version':x['published_version'],**json.loads(x['published'])[lang]} for x in rows]
 @bp.get(r.PREFIX+'/phase1/portal')
 def portal():
  lang=request.args.get('lang','en')
  if lang not in LOCALES:abort(400,'Choose a supported portal language.')
  query=request.args.get('q','').strip()[:100];found=[x for x in locations if query.lower() in ' '.join(x[1:]).lower()]
  return r.page('phase1-public.html',lang=lang,labels=LABELS[lang],articles=live(lang),locations=found,query=query)
 @bp.get(r.PREFIX+'/api/phase1/public-data')
 def data():
  lang=request.args.get('lang','en')
  if lang not in LOCALES:abort(400,'Unsupported language.')
  articles=live(lang)
  return {'synthetic':True,'language':lang,'published_entries':len(articles),'demo_zones':6,'programmes':sum(x['kind']=='programme' for x in articles),'notice':LABELS[lang][1]}
 @bp.get(r.PREFIX+'/phase1/cms')
 def admin():
  require('view')
  with db() as c:entries=[dict(x) for x in c.execute('SELECT id,kind,status,version,published_version FROM cms_entries ORDER BY updated DESC')]
  return r.page('phase1-cms.html',entries=entries,entry=None,locales=LOCALES,permissions=permissions())
 @bp.get(r.PREFIX+'/phase1/cms/<eid>')
 def edit(eid):
  require('view')
  with db() as c:
   row=c.execute('SELECT * FROM cms_entries WHERE id=?',(eid,)).fetchone()
   if not row:abort(404,'Entry not found.')
   past=[dict(x) for x in c.execute('SELECT version,action,actor,at,content FROM cms_history WHERE entry=? ORDER BY id DESC',(eid,))]
  return r.page('phase1-cms.html',entries=[],entry=dict(row),content=json.loads(row['draft']),history=past,locales=LOCALES,permissions=permissions())
 @bp.post(r.PREFIX+'/phase1/cms/save')
 def save():
  require('edit');content={}
  for lang in LOCALES:
   title=request.form.get(lang+'_title','').strip();body=request.form.get(lang+'_body','').strip()
   if not 3<=len(title)<=160 or not 10<=len(body)<=2000:abort(400,'Supply a title and body in all four languages within the stated lengths.')
   content[lang]={'title':title,'body':body}
  kind=request.form.get('kind')
  if kind not in ('programme','news','policy'):abort(400,'Choose a supported content type.')
  payload=json.dumps(content);eid=request.form.get('id') or 'DEMO-CMS-'+uuid.uuid4().hex[:12]
  with db() as c:
   c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT * FROM cms_entries WHERE id=?',(eid,)).fetchone()
   if row:
    if request.form.get('version')!=str(row['version']):abort(409,'The entry changed. Reload before saving.')
    c.execute("UPDATE cms_entries SET kind=?,draft=?,version=version+1,status='draft',author=?,reviewer=NULL,updated=? WHERE id=?",(kind,payload,g.user['sub'],r.stamp(),eid))
   else:c.execute("INSERT INTO cms_entries VALUES(?,?,?,1,'draft',?,NULL,NULL,NULL,?)",(eid,kind,payload,g.user['sub'],r.stamp()))
   history(c,c.execute('SELECT * FROM cms_entries WHERE id=?',(eid,)).fetchone(),'save')
  return redirect(r.PREFIX+'/phase1/cms/'+eid)
 @bp.post(r.PREFIX+'/phase1/cms/<eid>/<action>')
 def lifecycle(eid,action):
  require('review' if action=='review' else 'publish' if action in ('publish','archive') else 'edit')
  with db() as c:
   c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT * FROM cms_entries WHERE id=?',(eid,)).fetchone()
   if not row:abort(404,'Entry not found.')
   if request.form.get('version')!=str(row['version']):abort(409,'The entry changed. Reload before deciding.')
   if action=='submit' and row['status']=='draft':c.execute("UPDATE cms_entries SET status='in_review' WHERE id=?",(eid,))
   elif action=='review' and row['status']=='in_review':
    if row['author']==g.user['sub']:abort(403,'A different reviewer must review this content.')
    c.execute("UPDATE cms_entries SET status='reviewed',reviewer=? WHERE id=?",(g.user['sub'],eid))
   elif action=='publish' and row['status']=='reviewed':c.execute("UPDATE cms_entries SET status='published',published=draft,published_version=version WHERE id=?",(eid,))
   elif action=='archive' and row['status']!='archived':c.execute("UPDATE cms_entries SET status='archived' WHERE id=?",(eid,))
   else:abort(409,'This action is not available for the current entry status.')
   history(c,row,action)
  return redirect(r.PREFIX+'/phase1/cms/'+eid)
 r.app.register_blueprint(bp)
