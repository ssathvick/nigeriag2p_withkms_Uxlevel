"""Back up and apply the user-requested NSIPA documentation maintenance release."""
import datetime,json,re,shutil,sqlite3,subprocess
from pathlib import Path
src=Path(__file__).resolve().parents[1]; runtime=Path('/opt/openg2p-lab'); app=runtime/'registration';brand=runtime/'branding'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup=runtime/'knowledge-corrections'/stamp;backup.mkdir(parents=True,mode=0o700)
plan=json.loads((src/'knowledge/guidance-corrections.json').read_text())
targets=[(src/'knowledge/help.js',brand/'knowledge-help.js'),(src/'knowledge/context.js',brand/'knowledge-context.js'),(src/'knowledge/help.css',brand/'knowledge-help.css')]
# Patch branding text in the active templates and bundles, preserving unrelated deployed changes.
rx=re.compile(r'\bNigeria[\s-]*G2P\b(?![.\\\w-])',re.I)
patches={}
for folder in [app/'templates',app/'static',brand]:
 for p in folder.glob('*'):
  if p.suffix not in ['.js','.html','.css']:continue
  old=p.read_text();new=rx.sub('NSIPA',old)
  if new!=old:patches[p]=new
snippet=Path('/etc/nginx/snippets/iqs-brand.conf');patches[snippet]=re.sub(r'(knowledge-(?:help|context)\.(?:js|css)\?v=)[^"<> ]+',r'\g<1>nsipa-20261110',snippet.read_text())
for source,target in targets:patches[target]=source.read_text()
manifest=[]
for i,(p,content) in enumerate(patches.items()):
 saved=backup/str(i);shutil.copy2(p,saved);manifest.append({'target':str(p),'saved':str(saved)})
(backup/'files.json').write_text(json.dumps(manifest,indent=2))
db=sqlite3.connect(app/'intake.sqlite');db.row_factory=sqlite3.Row
with sqlite3.connect(backup/'intake.sqlite') as copy:db.backup(copy)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();actor='system:nsipa-context-maintenance'
note='User-requested context and NSIPA naming correction; maintenance publication, not an independent staff review.'
try:
 with db:
  for update in plan['updates']:
   row=db.execute('SELECT * FROM km_articles WHERE id=?',(update['id'],)).fetchone()
   assert json.loads(row['published'])==update['before'] and row['draft']==row['published'] and row['status']=='published','Concurrent guidance change; deployment stopped.'
   content=json.dumps(update['content'],ensure_ascii=False);version=row['version']+1
   db.execute('UPDATE km_articles SET draft=?,published=?,version=?,published_version=?,author=?,reviewer=NULL,review_note=?,updated=? WHERE id=?',(content,content,version,version,actor,note,now,row['id']))
   db.execute('INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,?,?,?,?,?,?)',(row['id'],version,'maintenance_publication',actor,now,content,note))
  for item in plan['new']:
   content=json.dumps({k:v for k,v in item.items() if k!='slug'},ensure_ascii=False)
   cur=db.execute("INSERT INTO km_articles(slug,module,stage,audience,draft,version,status,author,published,published_version,updated,review_note) VALUES(?,?,?,?,?,1,'published',?,?,1,?,?)",(item['slug'],item['module'],item['stage'],item['audience'],content,actor,content,now,note))
   db.execute('INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,1,?,?,?,?,?)',(cur.lastrowid,'maintenance_publication',actor,now,content,note))
  for p,content in patches.items():p.write_text(content)
  subprocess.run(['nginx','-t'],check=True)
except Exception:
 for item in manifest:shutil.copy2(item['saved'],item['target'])
 raise
# Keep bootstrap content aligned with the corrected published guidance.
for seed in [src/'knowledge-seed.json',src/'knowledge/seed.json',app/'knowledge-seed.json']:
 if not seed.exists():continue
 data=json.loads(seed.read_text());by_slug={u['slug']:u['content'] for u in plan['updates']}
 data['articles']=[{**a,**by_slug.get(a['slug'],{})} for a in data['articles']]
 existing={a['slug'] for a in data['articles']};data['articles'] += [a for a in plan['new'] if a['slug'] not in existing]
 seed.write_text(json.dumps(data,ensure_ascii=False,indent=2))
subprocess.run(['systemctl','reload','nginx'],check=True)
print(json.dumps({'backup':str(backup),'updated':len(plan['updates']),'added':len(plan['new']),'files':len(patches)}))
