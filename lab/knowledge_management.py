"""Versioned, plain-text knowledge guidance; permissions remain native."""
import json,re
from pathlib import Path
from flask import Blueprint,g,request,abort,redirect
SEED=json.loads(Path(__file__).with_name('knowledge-seed.json').read_text(encoding='utf-8'))
FIELDS=['module','stage','audience','title','purpose','steps','requirements','next_step','issues']
AUDIENCES=['all','citizen','officer','verifier','supervisor']
MODULES={m['id']:m['name'] for m in SEED['modules']}
def reference_metadata(item):
 from urllib.parse import urlparse
 sources=[]
 for source in item.get('sources',[]):
  url=source.get('url','');parsed=urlparse(url)
  if parsed.scheme=='https' and (parsed.hostname in ['docs.openg2p.org','nigeriag2p.com'] or parsed.hostname=='github.com' and parsed.path.startswith('/OpenG2P/openg2p-documentation/')):
   sources.append({'title':str(source.get('title','Reference'))[:160],'url':url[:1200]})
 result={'sources':sources[:8]} if sources else {}
 if item.get('scope') in ['upstream_reference','local_workflow']:result['scope']=item['scope']
 if re.fullmatch(r'\d{4}-\d{2}-\d{2}',item.get('sources_checked_on','')):result['sources_checked_on']=item['sources_checked_on']
 return result
def install(r):
 bp=Blueprint('knowledge',__name__)
 with r.db() as c:
  c.executescript("""CREATE TABLE IF NOT EXISTS km_articles(id INTEGER PRIMARY KEY,slug TEXT UNIQUE NOT NULL,module TEXT NOT NULL,stage TEXT NOT NULL,audience TEXT NOT NULL,draft TEXT NOT NULL,version INTEGER NOT NULL,status TEXT NOT NULL,author TEXT NOT NULL,reviewer TEXT,published TEXT,published_version INTEGER,updated TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS km_history(id INTEGER PRIMARY KEY,article INTEGER NOT NULL,version INTEGER NOT NULL,action TEXT NOT NULL,actor TEXT NOT NULL,at TEXT NOT NULL,content TEXT NOT NULL);""")
  for table,column in [('km_articles','review_note'),('km_history','note')]:
   if column not in {row[1] for row in c.execute('PRAGMA table_info('+table+')')}:c.execute('ALTER TABLE '+table+' ADD COLUMN '+column+" TEXT DEFAULT ''")
  for item in SEED['articles']:
   content=json.dumps({**{k:item[k] for k in FIELDS},**reference_metadata(item)});now=r.stamp();actor='system:documentation-import' if item.get('origin')=='system:documentation-import' else 'system:initial-guidance'
   cur=c.execute("INSERT OR IGNORE INTO km_articles(slug,module,stage,audience,draft,version,status,author,reviewer,published,published_version,updated) VALUES(?,?,?,?,?,1,'published',?,?,?,1,?)",(item['slug'],item['module'],item['stage'],item['audience'],content,actor,actor,content,now))
   if cur.rowcount:c.execute("INSERT INTO km_history(article,version,action,actor,at,content) VALUES(?,1,?,?,?,?)",(cur.lastrowid,'documentation_import' if actor=='system:documentation-import' else 'initial_guidance',actor,now,content))
 def permissions():
  roles=g.user.get('roles',[]) if g.user else [];staff=g.session.get('mode')=='staff'
  return {'edit':staff and (g.staff or any(role in roles for role in ['iqs-registration-officer','iqs-verification-officer','iqs-programme-supervisor'])),'review':staff and (g.staff or 'iqs-verification-officer' in roles),'publish':staff and (g.staff or 'iqs-programme-supervisor' in roles)}
 def require(action):
  r.require_user()
  if not permissions()[action]:abort(403,'Your account cannot perform this knowledge action.')
 def history(c,a,action,note=''):c.execute('INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,?,?,?,?,?,?)',(a['id'],a['version'],action,g.user['sub'],r.stamp(),a['draft'],note))
 def published():
  result=[]
  for row in r.rows("SELECT * FROM km_articles WHERE published IS NOT NULL AND status!='archived' ORDER BY module,stage,audience"):
   result.append({'id':row['id'],'slug':row['slug'],'version':row['published_version'],**json.loads(row['published'])})
  return result
 @bp.get(r.PREFIX+'/api/knowledge')
 def public_api():
  articles=published();module=request.args.get('module');audience=request.args.get('audience','all')
  if module:articles=[a for a in articles if a['module']==module]
  if audience not in AUDIENCES:abort(400,'Unknown audience')
  if request.args.get('include_roles')!='1':articles=[a for a in articles if a['audience'] in ['all',audience]]
  response=r.app.make_response({'articles':articles,'modules':SEED['modules'],'audiences':AUDIENCES,'notice':'Published task guidance is public. Role filters do not grant permissions.'})
  origin=request.headers.get('Origin','');host=origin.removeprefix('https://')
  if origin.startswith('https://') and (host=='nigeriag2p.com' or re.fullmatch(r'[a-z0-9-]+\.nigeriag2p\.com',host)):response.headers['Access-Control-Allow-Origin']=origin;response.headers['Vary']='Origin'
  return response
 @bp.get(r.PREFIX+'/knowledge')
 def library():
  articles=published();total_published=len(articles);source_guides=sum(bool(a.get('sources')) for a in articles);q=request.args.get('q','').strip().lower();module=request.args.get('module','');audience=request.args.get('audience','all')
  if module:articles=[a for a in articles if a['module']==module]
  if audience not in AUDIENCES:abort(400)
  articles=[a for a in articles if a['audience'] in ['all',audience] and (not q or q in ' '.join(str(a[k]) for k in FIELDS).lower())]
  if audience!='all':
   choices={}
   for a in articles:
    key=(a['module'],a['stage'])
    if key not in choices or a['audience']==audience:choices[key]=a
   articles=list(choices.values())
  return r.page('knowledge-library.html',articles=articles,modules=MODULES,audiences=AUDIENCES,perms=permissions(),total_published=total_published,source_guides=source_guides,q=request.args.get('q',''),module=module,audience=audience)
 @bp.get(r.PREFIX+'/knowledge/admin')
 def admin():
  if not g.user:return redirect(r.PREFIX+'/login?mode=staff&knowledge=1')
  require('edit');items=r.rows('SELECT * FROM km_articles ORDER BY updated DESC')
  for a in items:a['content']=json.loads(a['draft'])
  return r.page('knowledge-admin.html',items=items,perms=permissions())
 @bp.get(r.PREFIX+'/knowledge/admin/new')
 @bp.get(r.PREFIX+'/knowledge/admin/<int:aid>')
 def editor(aid=None):
  require('edit');a=r.one('SELECT * FROM km_articles WHERE id=?',(aid,)) if aid else None
  if aid and not a:abort(404)
  return r.page('knowledge-editor.html',article=a,content=json.loads(a['draft']) if a else {},modules=MODULES,audiences=AUDIENCES,perms=permissions(),history=r.rows('SELECT id,version,action,actor,at,note FROM km_history WHERE article=? ORDER BY id DESC',(aid,)) if aid else [])
 @bp.post(r.PREFIX+'/knowledge/admin/save')
 def save():
  require('edit');aid=request.form.get('id');data={k:request.form.get(k,'').strip() for k in FIELDS}
  if data['module'] not in MODULES or data['audience'] not in AUDIENCES:abort(400,'Choose a valid module and audience.')
  if any(not data[k] for k in FIELDS) or any(len(v)>6000 for v in data.values()) or len(data['title'])>160 or len(data['stage'])>160:abort(400,'Complete every field; keep guidance concise (maximum 6000 characters per field).')
  actor=g.user['sub'];now=r.stamp();content=json.dumps(data)
  with r.db() as c:
   c.execute('BEGIN IMMEDIATE')
   if aid:
    a=c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone()
    if not a:abort(404)
    if request.form.get('version')!=str(a['version']):abort(409,'Guidance changed. Reload before saving.')
    content=json.dumps({**data,**reference_metadata(json.loads(a['draft']))});version=a['version']+1;c.execute("UPDATE km_articles SET module=?,stage=?,audience=?,draft=?,version=?,status='draft',author=?,reviewer=NULL,updated=? WHERE id=?",(data['module'],data['stage'],data['audience'],content,version,actor,now,aid))
   else:
    import secrets
    slug=re.sub('[^a-z0-9]+','-',data['title'].lower()).strip('-')+'-'+secrets.token_hex(4)
    aid=c.execute("INSERT INTO km_articles(slug,module,stage,audience,draft,version,status,author,updated) VALUES(?,?,?,?,?,1,'draft',?,?)",(slug,data['module'],data['stage'],data['audience'],content,actor,now)).lastrowid
   a=dict(c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone());history(c,a,'saved')
  return redirect(r.PREFIX+'/knowledge/admin/'+str(aid))
 @bp.post(r.PREFIX+'/knowledge/admin/<int:aid>/<action>')
 def transition(aid,action):
  if action not in ['submit','review','return','publish','archive','restore']:abort(404)
  require('review' if action in ['review','return'] else 'publish' if action in ['publish','archive','restore'] else 'edit')
  note=request.form.get('reason','').strip()
  if len(note)>2000 or (action=='return' and len(note)<10):abort(400,'Provide a useful return reason (10–2000 characters).')
  with r.db() as c:
   c.execute('BEGIN IMMEDIATE');row=c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone()
   if not row:abort(404)
   a=dict(row);actor=g.user['sub']
   if request.form.get('version')!=str(a['version']):abort(409,'Guidance changed. Reload before continuing.')
   allowed={'submit':['draft'],'review':['in_review'],'return':['in_review'],'publish':['reviewed'],'archive':['published','draft','in_review','reviewed'],'restore':['archived']}
   if a['status'] not in allowed[action]:abort(409,'This action is not available in the current status.')
   if action in ['review','return'] and a['author']==actor:abort(403,'A different staff member must review your guidance.')
   if action=='publish' and (not a['reviewer'] or a['reviewer']==a['author']):abort(403,'An independent review is required before publication.')
   if action=='publish':c.execute("UPDATE km_articles SET published=draft,published_version=version,status='published',updated=? WHERE id=?",(r.stamp(),aid))
   else:
    status={'submit':'in_review','review':'reviewed','return':'draft','archive':'archived','restore':'draft'}[action]
    c.execute('UPDATE km_articles SET status=?,reviewer=?,updated=? WHERE id=?',(status,actor if action=='review' else None,r.stamp(),aid))
    if action=='restore':c.execute('UPDATE km_articles SET published=NULL,published_version=NULL WHERE id=?',(aid,))
   if action in ['review','return']:c.execute('UPDATE km_articles SET review_note=? WHERE id=?',(note,aid))
   history(c,a,action,note)
  return redirect(r.PREFIX+'/knowledge/admin/'+str(aid))
 @bp.get(r.PREFIX+'/knowledge/admin/<int:aid>/history/<int:hid>')
 def revision(aid,hid):
  require('edit');row=r.one('SELECT * FROM km_history WHERE article=? AND id=?',(aid,hid))
  if not row:abort(404)
  return r.page('knowledge-revision.html',revision=row,content=json.loads(row['content']),article=r.one('SELECT * FROM km_articles WHERE id=?',(aid,)),perms=permissions())
 @bp.post(r.PREFIX+'/knowledge/admin/<int:aid>/restore-version/<int:hid>')
 def restore_version(aid,hid):
  require('edit')
  with r.db() as c:
   c.execute('BEGIN IMMEDIATE');a=c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone();old=c.execute('SELECT * FROM km_history WHERE article=? AND id=?',(aid,hid)).fetchone()
   if not a or not old:abort(404)
   if request.form.get('version')!=str(a['version']):abort(409,'Guidance changed. Reload before restoring.')
   content=json.loads(old['content']);c.execute("UPDATE km_articles SET module=?,stage=?,audience=?,draft=?,version=version+1,status='draft',author=?,reviewer=NULL,updated=? WHERE id=?",(content['module'],content['stage'],content['audience'],old['content'],g.user['sub'],r.stamp(),aid))
   if a['status']=='archived':c.execute('UPDATE km_articles SET published=NULL,published_version=NULL WHERE id=?',(aid,))
   history(c,dict(c.execute('SELECT * FROM km_articles WHERE id=?',(aid,)).fetchone()),'restore_version')
  return redirect(r.PREFIX+'/knowledge/admin/'+str(aid))
 r.app.register_blueprint(bp)
