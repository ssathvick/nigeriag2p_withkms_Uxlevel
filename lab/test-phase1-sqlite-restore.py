"""Restore two active SQLite backups into private temporary copies, never live data."""
import datetime as dt,json,sqlite3,sys,tempfile
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
results=[]
with tempfile.TemporaryDirectory(prefix='phase1-restore-',dir=r.ROOT/'phase1-private-tests') as tmp:
 for name in ['intake.sqlite','phase1-sandbox.sqlite']:
  source=r.ROOT/name;backup=Path(tmp)/(name+'.backup');restored=Path(tmp)/(name+'.restored')
  with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as c,sqlite3.connect(backup) as b:c.backup(b)
  with sqlite3.connect(backup) as b,sqlite3.connect(restored) as target:b.backup(target)
  with sqlite3.connect(backup) as b,sqlite3.connect(restored) as target:
   integrity=target.execute('PRAGMA integrity_check').fetchone()[0]
   tables=[x[0] for x in b.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
   assert all(__import__('re').fullmatch(r'[a-z_]+',t) for t in tables)
   match=all(b.execute('SELECT COUNT(*) FROM '+t).fetchone()==target.execute('SELECT COUNT(*) FROM '+t).fetchone() for t in tables)
   indexes=b.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'").fetchone()==target.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'").fetchone()
  results.append({'database':name,'integrity':integrity,'table_counts_preserved':match,'indexes_preserved':indexes,'status':'passed' if integrity=='ok' and match and indexes else 'failed'})
report={'scope':'SQLite backup and isolated restore integrity only; no live database replacement','checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'databases':results,'private_copies_removed':True,'status':'passed' if all(x['status']=='passed' for x in results) else 'failed','limitation':'Whole-stack PostgreSQL restore, service recovery and RPO/RTO acceptance remain pending.'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/sqlite-restore.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['status']=='passed'
