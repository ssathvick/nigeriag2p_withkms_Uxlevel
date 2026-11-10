"""Apply inspected, guarded KMS and owned experience improvements."""
from pathlib import Path
root=Path(__file__).parent
def change(path,old,new):
 p=root/path;s=p.read_text(encoding='utf-8')
 if new in s:return
 assert s.count(old)==1 or (old=="status='draft',author=?,reviewer=NULL,updated=? WHERE id=?" and s.count(old)==2),(path,old[:80]);p.write_text(s.replace(old,new),encoding='utf-8')
change('knowledge_management.py','import json,re','import json,re,datetime,unicodedata,math\nfrom urllib.parse import urlencode')
anchor=' def published():\n'
helper=''' def readable(content):
  if content.get('visibility','public')=='public':return True
  if not g.user or g.session.get('mode')!='staff':return False
  roles=set(g.user.get('roles',[]))
  if 'iqs-intake-reviewer' in roles:return True
  required={'officer':'iqs-registration-officer','verifier':'iqs-verification-officer','supervisor':'iqs-programme-supervisor'}
  audience=content.get('audience','all')
  return bool(roles.intersection(required.values())) if audience in ('all','citizen') else required.get(audience) in roles
 def governance(form,previous=None):
  previous=previous or {};visibility=form.get('visibility',previous.get('visibility','public'));due=form.get('review_due',previous.get('review_due','')).strip()
  if visibility not in ('public','staff'):abort(400,'Choose public or staff-only visibility.')
  if due:
   try:datetime.date.fromisoformat(due)
   except ValueError:abort(400,'Use a valid review date.')
  return {'visibility':visibility,'review_due':due}
 def normalized(value):
  return ''.join(c for c in unicodedata.normalize('NFKD',value.casefold()) if not unicodedata.combining(c))
 def matches(article,query):
  words=normalized(query).split();text=normalized(' '.join(str(article[k]) for k in FIELDS))
  return all(word in text for word in words)
'''
change('knowledge_management.py',anchor,helper+anchor)
change('knowledge_management.py',"   result.append({'id':row['id'],'slug':row['slug'],'version':row['published_version'],**json.loads(row['published'])})", "   content=json.loads(row['published'])\n   if readable(content):result.append({'id':row['id'],'slug':row['slug'],'version':row['published_version'],**content})")
change('knowledge_management.py',"  if module:articles=[a for a in articles if a['module']==module]\n  if audience not in AUDIENCES:abort(400,'Unknown audience')", "  if module and module not in MODULES:abort(400,'Unknown service')\n  if module:articles=[a for a in articles if a['module']==module]\n  if audience not in AUDIENCES:abort(400,'Unknown audience')")
change('knowledge_management.py',"  response=r.app.make_response({'articles':articles", "  query=request.args.get('q','').strip()\n  if len(query)>160:abort(400,'Keep searches under 160 characters.')\n  if query:articles=[a for a in articles if matches(a,query)]\n  response=r.app.make_response({'articles':articles")
change('knowledge_management.py',"  return response\n @bp.get(r.PREFIX+'/knowledge')", "  response.headers['Cache-Control']='private, no-store'\n  response.headers['Vary']='Cookie, Origin'\n  return response\n @bp.get(r.PREFIX+'/knowledge')")
change('knowledge_management.py',"  articles=[a for a in articles if a['audience'] in ['all',audience] and (not q or q in ' '.join(str(a[k]) for k in FIELDS).lower())]", "  if len(q)>160 or module and module not in MODULES:abort(400,'Choose a service and a search of at most 160 characters.')\n  articles=[a for a in articles if a['audience'] in ['all',audience] and matches(a,q)]")
old="  return r.page('knowledge-library.html',articles=articles,modules=MODULES,audiences=AUDIENCES,perms=permissions(),total_published=total_published,source_guides=source_guides,q=request.args.get('q',''),module=module,audience=audience)"
new="""  if q:articles.sort(key=lambda a:sum(normalized(a['title']).count(w)*3 for w in normalized(q).split()),reverse=True)
  total_matches=len(articles)
  try:page_number=int(request.args.get('page','1'))
  except ValueError:abort(400,'Use a valid page number.')
  pages=max(1,math.ceil(total_matches/12))
  if not 1<=page_number<=pages:abort(400,'This result page does not exist.')
  articles=articles[(page_number-1)*12:page_number*12]
  def page_url(n):return r.PREFIX+'/knowledge?'+urlencode({'q':request.args.get('q',''),'module':module,'audience':audience,'page':n})
  return r.page('knowledge-library.html',articles=articles,modules=MODULES,audiences=AUDIENCES,perms=permissions(),total_published=total_published,source_guides=source_guides,q=request.args.get('q',''),module=module,audience=audience,total_matches=total_matches,page_number=page_number,pages=pages,previous_url=page_url(page_number-1) if page_number>1 else None,next_url=page_url(page_number+1) if page_number<pages else None)
 @bp.get(r.PREFIX+'/knowledge/<int:aid>')
 def article_page(aid):
  item=next((a for a in published() if a['id']==aid),None)
  if not item:abort(404)
  return r.page('knowledge-article.html',article=item,modules=MODULES)
 @bp.get(r.PREFIX+'/knowledge/<int:aid>/export')
 def export(aid):
  item=next((a for a in published() if a['id']==aid),None)
  if not item:abort(404)
  body=item['title']+'\\nPublished version '+str(item['version'])+'\\n\\n'+'\\n\\n'.join(k.replace('_',' ').title()+'\\n'+item[k] for k in FIELDS if k not in ('title','module','audience','stage'))
  response=r.app.make_response(body);response.headers['Content-Type']='text/plain; charset=utf-8';response.headers['Content-Disposition']='attachment; filename="knowledge-'+str(aid)+'-v'+str(item['version'])+'.txt"';response.headers['Cache-Control']='private, no-store';return response"""
change('knowledge_management.py',old,new)
change('knowledge_management.py',"  actor=g.user['sub'];now=r.stamp();content=json.dumps(data)","  actor=g.user['sub'];now=r.stamp();content=json.dumps({**data,**governance(request.form)})")
change('knowledge_management.py',"    content=json.dumps({**data,**reference_metadata(json.loads(a['draft']))});version=", "    previous=json.loads(a['draft']);content=json.dumps({**data,**reference_metadata(previous),**governance(request.form,previous)});version=")
change('knowledge_management.py',"status='draft',author=?,reviewer=NULL,updated=? WHERE id=?", "status='draft',author=?,reviewer=NULL,review_note='',updated=? WHERE id=?")
change('registration-ui/knowledge-library.html','<p>{{articles|length}} published guidance entries</p>','<p role="status">{{total_matches}} matching entries · Page {{page_number}} of {{pages}}</p><nav aria-label="Knowledge results pages">{% if previous_url %}<a href="{{previous_url}}">Previous results</a>{% endif %}{% if next_url %}<a href="{{next_url}}">Next results</a>{% endif %}</nav>')
change('registration-ui/knowledge-library.html','<small>Published version {{a.version}}</small>','<small>Published version {{a.version}} · {{a.visibility|default("public")}} guidance</small><p><a href="{{prefix}}/knowledge/{{a.id}}">Open this guide</a> · <a href="{{prefix}}/knowledge/{{a.id}}/export">Download plain text</a></p>')
change('registration-ui/knowledge-library.html','<input name="q" value="{{q}}" placeholder=', '<input name="q" maxlength="160" value="{{q}}" placeholder=')
change('registration-ui/knowledge-editor.html','<button>Save draft</button>', '<label>Visibility<select name="visibility"><option value="public" {% if content.visibility|default("public")=="public" %}selected{% endif %}>Public task guidance</option><option value="staff" {% if content.visibility=="staff" %}selected{% endif %}>Staff only for the selected audience</option></select></label><label>Next content review date<input type="date" name="review_due" value="{{content.review_due or \'\'}}"></label><button>Save draft</button>')
change('registration-ui/knowledge-editor.html','Published content is public. Keep personal data, credentials and confidential procedures out of guidance.', 'Choose public or staff-only visibility. Staff-only content requires an authorised matching staff role. Keep credentials and personal beneficiary data out of all guidance.')
change('registration-ui/knowledge-admin.html','Published guidance is visible to all users; include task instructions only.', 'Published public guidance is visible to everyone. Staff-only guidance requires an authorised matching staff role. Review visibility before publishing.')
change('registration-ui/base.html','<title>IQS Nigeria • Registration</title>', '<title>{% block title %}IQS Nigeria • Registration{% endblock %}</title>')
change('registration-ui/base.html','<body><header>', '<body><a class="experience-skip" href="#experience-main">Skip to main content</a><header>')
change('registration-ui/base.html','<main>{% block content %}', '<main id="experience-main" tabindex="-1">{% block content %}')
change('registration-ui/base.html','</head><body>', '<link rel="stylesheet" href="{{prefix}}/static/experience.css?v=kms-ux-20261012"></head><body>')
change('registration-ui/workspace.html','</head><body>', '<link rel="stylesheet" href="{{prefix}}/static/experience.css?v=kms-ux-20261012"></head><body>')
change('persona-ui/src/main.jsx',"import React,{useState,useEffect}","import React,{useState,useEffect,useRef}")
change('persona-ui/src/main.jsx','async function load(){', '''const confirmationRef=useRef(null);
const dirty=Boolean(role==='officer'&&profileForDraft()&&edit&&(edit.household_name!==profileForDraft().name||edit.community!==profileForDraft().community||Number(edit.income)!==Number(profileForDraft().income)));
function profileForDraft(){return data?.profiles.find(p=>p.sub===selected)}
function leave(){return !dirty||window.confirm('Discard unsaved household corrections?')}
useEffect(()=>{const guard=e=>{if(dirty){e.preventDefault();e.returnValue=''}};window.addEventListener('beforeunload',guard);return()=>window.removeEventListener('beforeunload',guard)},[dirty]);
useEffect(()=>{if(confirming)confirmationRef.current?.querySelector('button')?.focus()},[confirming]);
async function load(){''')
change('persona-ui/src/main.jsx','function switchRole(next){setRole(next);','function switchRole(next){if(busy||!leave())return;setRole(next);')
change('persona-ui/src/main.jsx','function open(p){setConfirming(false);','function open(p){if(busy||!leave())return;setConfirming(false);')
change('persona-ui/src/main.jsx',"return <><div className={'modebar", "return <><a className=\"experience-skip\" href=\"#workspace-main\">Skip to main content</a><div className={'modebar")
change('persona-ui/src/main.jsx','</aside><main><header>', '</aside><main id="workspace-main" tabIndex="-1" aria-busy={busy}><header>')
change('persona-ui/src/main.jsx',"onClick={()=>setView('work')}","aria-pressed={view==='work'} onClick={()=>{if(!busy&&leave())setView('work')}}")
change('persona-ui/src/main.jsx',"onClick={()=>{setView('applications');setSelected(null)}}", "aria-pressed={view==='applications'} onClick={()=>{if(busy||!leave())return;setView('applications');setSelected(null)}}")
change('persona-ui/src/main.jsx',"onClick={()=>setView('activity')}","aria-pressed={view==='activity'} onClick={()=>{if(!busy&&leave())setView('activity')}}")
change('persona-ui/src/main.jsx',"onClick={()=>{setSelected(null);setChecks([false,false,false])}}", "onClick={()=>{if(busy||!leave())return;setSelected(null);setChecks([false,false,false]);setEdit(null)}}")
change('persona-ui/src/main.jsx','{confirming&&<div className="alert"><strong>Confirm registration approval</strong>', '{confirming&&<div className="alert" ref={confirmationRef} role="group" aria-labelledby="approval-confirm-title"><strong id="approval-confirm-title">Confirm registration approval</strong>')
change('knowledge/help.js',"panel.addEventListener('keydown',e=>{if(e.key==='Escape')hide()});", "panel.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();hide()}});")
print('Guarded KMS and UX source changes prepared.')
