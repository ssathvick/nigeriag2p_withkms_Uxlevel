from pathlib import Path
p=Path('knowledge_management.py');s=p.read_text(encoding='utf-8')
s=s.replace("MODULES={m['id']:m['name'] for m in SEED['modules']}","""MODULES={m['id']:m['name'] for m in SEED['modules']}
def reference_metadata(item):
 from urllib.parse import urlparse
 sources=[]
 for source in item.get('sources',[]):
  url=source.get('url','');parsed=urlparse(url)
  if parsed.scheme=='https' and (parsed.hostname in ['docs.openg2p.org','nigeriag2p.com'] or parsed.hostname=='github.com' and parsed.path.startswith('/OpenG2P/openg2p-documentation/')):
   sources.append({'title':str(source.get('title','Reference'))[:160],'url':url[:1200]})
 result={'sources':sources[:8]} if sources else {}
 if item.get('scope') in ['upstream_reference','local_workflow']:result['scope']=item['scope']
 if re.fullmatch(r'\\d{4}-\\d{2}-\\d{2}',item.get('sources_checked_on','')):result['sources_checked_on']=item['sources_checked_on']
 return result""")
s=s.replace("content=json.dumps({k:item[k] for k in FIELDS});now=r.stamp()","content=json.dumps({**{k:item[k] for k in FIELDS},**reference_metadata(item)});now=r.stamp();actor='system:documentation-import' if item.get('origin')=='system:documentation-import' else 'system:initial-guidance'")
s=s.replace("'published','system:initial-guidance','system:initial-guidance',?,1,?)","'published',?,?,?,1,?)").replace("item['audience'],content,content,now)","item['audience'],content,actor,actor,content,now)")
s=s.replace("VALUES(?,1,'initial_guidance','system:initial-guidance',?,?)\",(cur.lastrowid,now,content)","VALUES(?,1,?,?,?,?)\",(cur.lastrowid,'documentation_import' if actor=='system:documentation-import' else 'initial_guidance',actor,now,content)")
s=s.replace("articles=published();q=request.args", "articles=published();total_published=len(articles);source_guides=sum(bool(a.get('sources')) for a in articles);q=request.args")
s=s.replace("perms=permissions(),q=request.args", "perms=permissions(),total_published=total_published,source_guides=source_guides,q=request.args")
s=s.replace("version=a['version']+1;c.execute", "content=json.dumps({**data,**reference_metadata(json.loads(a['draft']))});version=a['version']+1;c.execute")
p.write_text(s,encoding='utf-8')
p=Path('registration-ui/knowledge-library.html');s=p.read_text(encoding='utf-8').replace('Short guidance for each service and workflow stage. Your account permissions determine the actions available.','Task guidance for each service and workflow stage. Local guides describe NigeriaG2P; upstream references may describe other releases. Your account determines available actions.').replace('<p><a href="{{prefix}}/workspace">','<p><strong>{{total_published}} published entries across {{modules|length}} services · {{source_guides}} source-linked guides</strong></p><p><a href="{{prefix}}/workspace">')
s=s.replace('<p>{{a.purpose}}</p>',"{% if a.scope %}<p><strong>{{'NigeriaG2P local workflow' if a.scope=='local_workflow' else 'Upstream reference — confirm feature availability'}}</strong></p>{% endif %}<p>{{a.purpose}}</p>")
s=s.replace('<small>Published version {{a.version}}</small>',"{% if a.sources %}<h3>References</h3><ul>{% for source in a.sources %}<li><a href=\"{{source.url}}\" target=\"_blank\" rel=\"noopener noreferrer\">{{source.title}}</a></li>{% endfor %}</ul>{% if a.sources_checked_on %}<p>Sources checked: {{a.sources_checked_on}}</p>{% endif %}{% endif %}<small>Published version {{a.version}}</small>")
p.write_text(s,encoding='utf-8')
p=Path('knowledge/help.js');s=p.read_text(encoding='utf-8');needle="const version=document.createElement('small');version.textContent='Published version '+a.version;"
s=s.replace(needle,"if(a.scope==='upstream_reference'){const note=document.createElement('p');note.textContent='Upstream reference: confirm this feature exists in your installed release.';body.append(note)}if(a.sources?.length){const refs=document.createElement('p');refs.textContent='References: ';for(const ref of a.sources){if(!/^https:\\/\\/(docs\\.openg2p\\.org|nigeriag2p\\.com|github\\.com)\\//.test(ref.url))continue;const link=document.createElement('a');link.href=ref.url;link.textContent=ref.title;link.target='_blank';link.rel='noopener noreferrer';refs.append(link,document.createElement('br'))}body.append(refs)}"+needle)
p.write_text(s,encoding='utf-8')
p=Path('local_ai.py');s=p.read_text(encoding='utf-8').replace('If guidance is insufficient, say so.','If guidance is insufficient, say so. Articles labelled upstream_reference describe upstream capabilities; never claim those features are installed locally. Explain that their availability must be confirmed. Local_workflow articles describe the NigeriaG2P screens.');p.write_text(s,encoding='utf-8')
p=Path('install-knowledge.py');s=p.read_text().replace("'v=km7',s)","'v=km8',s)");p.write_text(s,encoding='utf-8')
