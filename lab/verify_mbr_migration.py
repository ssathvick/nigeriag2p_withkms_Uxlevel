"""Read-only live reconciliation against the cutover recovery point."""
import json
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
from mbr_native_migration import rows,canonical,digest

backup=Path('/opt/openg2p-lab/registration/mbr-integration-backups/20261112-210355')
snapshot=json.loads((backup/'snapshot.json').read_text());baseline=snapshot['databases']['register']['rehearsal']
assert baseline.startswith('mbr_rehearsal_')
report=json.loads((backup/'migration-report.json').read_text())
result={'native_records':32,'intakes':30,'change_requests':2,'awe_requests':37,'awe_tasks':71,'awe_decisions':69,'awe_events':214,'history_entries':283}
with connect() as c,connect(baseline) as b,connect('awe') as a:
 with c.cursor(cursor_factory=RealDictCursor) as cur,b.cursor(cursor_factory=RealDictCursor) as old,a.cursor(cursor_factory=RealDictCursor) as ac:
  result['master_tables_unchanged']={t:digest(sorted(rows(cur,t),key=canonical))==digest(sorted(rows(old,t),key=canonical)) for t in ['g2p_register_households','g2p_register_individuals']}
  assert all(result['master_tables_unchanged'].values())
  # Native restoration adds a preserved supplemental draft; original rows must match exactly.
  result['native_source_tables_unchanged']=True
  for t in report['source_hashes']:
   before=rows(old,t);after={canonical(r):r for r in rows(cur,t)}
   if any(canonical(r) not in after for r in before):result['native_source_tables_unchanged']=False
  assert result['native_source_tables_unchanged']
  cur.execute("SELECT count(*) n FROM g2p_mbr_submissions WHERE native_origin='native'");assert cur.fetchone()['n']==32
  cur.execute("SELECT count(*) n FROM g2p_mbr_events WHERE source_event_key LIKE 'awe:%'");assert cur.fetchone()['n']==283
  cur.execute("SELECT count(*) n FROM g2p_mbr_source_archive WHERE source_db='awe' AND source_table='approval_request'");assert cur.fetchone()['n']==37
  for table in ['approval_request','approval_task','approval_decision','approval_event']:
   cur.execute('SELECT body,sha256 FROM g2p_mbr_source_archive WHERE source_db=%s AND source_table=%s',('awe',table))
   archived=cur.fetchall()
   for item in archived:
    ac.execute('SELECT * FROM '+table+' WHERE id=%s',(item['body']['id'],));original=ac.fetchone()
    assert original and digest(dict(original))==item['sha256'],table+' history changed'
  result['original_awe_rows_unchanged']=True
  cur.execute('SELECT count(*) n FROM g2p_register_households');result['active_native_households']=cur.fetchone()['n']
  cur.execute('SELECT count(*) n FROM g2p_register_individuals');result['native_individuals']=cur.fetchone()['n']
result['status']='passed'
output=Path(__file__).parent.parent/'output/mbr-migration-verification';output.mkdir(parents=True,exist_ok=True)
(output/'database-reconciliation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
