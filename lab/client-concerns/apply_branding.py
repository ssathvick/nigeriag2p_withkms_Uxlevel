from pathlib import Path
import json,re,sys,sqlite3,datetime,shutil
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab');backup=Path('/opt/openg2p-lab/backups')/('client-concerns-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
(src/'client-concerns/backup-location.txt').write_text(str(backup))
with sqlite3.connect(r.ROOT/'intake.sqlite') as c,sqlite3.connect(backup/'intake.sqlite') as b:c.backup(b)
for name in ['registration_app.py','registration_workspaces.py']:shutil.copy2(r.ROOT/name,backup/name)
shutil.copytree(r.ROOT/'templates',backup/'templates');shutil.copytree('/opt/openg2p-lab/branding',backup/'branding')
patterns=[(r'(?:Modern|Unified|National) social registry','Master Beneficiary Registry'),(r'(?:OpenG2P|NSIPA) Reference Registry','Master Beneficiary Registry'),(r'Social registry administration','Master Beneficiary Registry administration'),(r'\bNigeria\s*G2P\b(?![.])','NSIPA Unified G2P'),(r'\bNCPA\b','NSIPA')]
def clean(s):
 for a,b in patterns:s=re.sub(a,b,s,flags=re.I)
 return s
files=list((src/'persona-ui/src').glob('*.js'))+list((src/'persona-ui/src').glob('*.jsx'))+list((src/'registration-ui').glob('*.html'))+[src/'knowledge-seed.json',src/'knowledge/seed.json',r.ROOT/'knowledge-seed.json']
for p in files:
 text=p.read_text();updated=clean(text)
 if text!=updated:p.write_text(updated)
with r.pg('register') as c:
 with c.cursor() as cur:
  cur.execute('SELECT row_to_json(t) FROM g2p_registry_configuration t');(backup/'registry-config.json').write_text(json.dumps(cur.fetchall(),default=str))
  cur.execute("UPDATE g2p_registry_configuration SET registry_name='Master Beneficiary Registry'")
  cur.execute('SELECT form_id,form_description FROM g2p_intake_form_definitions');old=cur.fetchall();(backup/'intake-descriptions.json').write_text(json.dumps(old))
  for key,description in old:cur.execute('UPDATE g2p_intake_form_definitions SET form_description=%s WHERE form_id=%s',(clean(description),key))
with r.db() as c:
 for row in c.execute('SELECT * FROM km_articles').fetchall():
  published=row['published'];draft=row['draft'];new=clean(published or '')
  if new==(published or ''):continue
  version=row['version']+1;note='Client requested Master Beneficiary Registry terminology.'
  c.execute('UPDATE km_articles SET published=?,draft=?,version=?,published_version=?,updated=? WHERE id=?',(new,clean(draft),version,version,r.stamp(),row['id']))
  c.execute('INSERT INTO km_history(article,version,action,actor,at,content,note) VALUES(?,?,?,?,?,?,?)',(row['id'],version,'maintenance_publication','system:client-concerns',r.stamp(),new,note))
print('Branding and published guide terminology updated. Private backup:',backup)

