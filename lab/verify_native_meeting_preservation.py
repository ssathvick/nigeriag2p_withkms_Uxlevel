"""Read-only comparison of every archived native data row and AWE history row."""
import json
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
from mbr_native_migration import canonical,digest
result={'status':'passed','native_rows_verified':0,'awe_rows_verified':0,'tables':{},'failures':[]}
baseline=json.loads(Path('/opt/openg2p-lab/registration/mbr-integration-backups/20261112-210355/snapshot.json').read_text())['databases']['register']['rehearsal']
with connect(baseline) as old,connect() as current:
 with old.cursor(cursor_factory=RealDictCursor) as oq,current.cursor(cursor_factory=RealDictCursor) as cq:
  oq.execute("SELECT DISTINCT table_name FROM information_schema.columns WHERE table_schema='public' AND column_name='internal_record_id' AND table_name LIKE 'g2p_register_%' ORDER BY table_name")
  tables=[r['table_name'] for r in oq.fetchall()]
  for table in tables:
   oq.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier(table)));before=oq.fetchall();cq.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier(table)));after=cq.fetchall()
   # History can have several versions for one record, so compare complete original row values.
   expected={canonical(dict(r)) for r in before};keys=list(before[0]) if before else []
   actual={canonical({k:r.get(k) for k in keys}) for r in after}
   if not expected<=actual:result['failures'].append({'database':'register','table':table,'missing_original_rows':len(expected-actual)})
   result['tables']['baseline.'+table]=len(before);result['native_rows_verified']+=len(before)
with connect() as c,connect('awe') as a:
 with c.cursor(cursor_factory=RealDictCursor) as q,a.cursor(cursor_factory=RealDictCursor) as aq:
  q.execute("SELECT source_db,source_table,body,sha256 FROM g2p_mbr_source_archive ORDER BY source_db,source_table")
  archived=q.fetchall();pks={}
  for item in archived:
   database,table,body=item['source_db'],item['source_table'],item['body'];cursor=aq if database=='awe' else q
   # Form metadata intentionally gains fields; original business data and histories do not change.
   if database!='awe' and not (table.startswith(('g2p_intake_form_','g2p_register_history_')) or table in ['g2p_register_households','g2p_register_individuals']):continue
   if table in ['g2p_intake_form_definitions','g2p_intake_form_ui_tabs','g2p_intake_form_ui_tab_sections']:continue
   key=(database,table)
   if key not in pks:
    cursor.execute("SELECT a.attname FROM pg_index i JOIN pg_attribute a ON a.attrelid=i.indrelid AND a.attnum=ANY(i.indkey) WHERE i.indrelid=%s::regclass AND i.indisprimary ORDER BY a.attnum",(table,));pks[key]=[r['attname'] for r in cursor.fetchall()]
   keys=pks[key]
   if not keys:raise AssertionError('No primary key for preserved table '+table)
   cursor.execute(sql.SQL('SELECT * FROM {} WHERE {}').format(sql.Identifier(table),sql.SQL(' AND ').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in keys)),[body[k] for k in keys]);current=cursor.fetchone()
   if not current or digest({k:current.get(k) for k in body})!=item['sha256']:result['failures'].append({'database':database,'table':table,'key':{k:body[k] for k in keys}})
   result['awe_rows_verified' if database=='awe' else 'native_rows_verified']+=1;result['tables'][database+'.'+table]=result['tables'].get(database+'.'+table,0)+1
  for table,key in [('g2p_register_households','households'),('g2p_register_individuals','individuals')]:q.execute('SELECT count(*) AS n FROM '+table);result[key]=q.fetchone()['n']
if result['failures']:result['status']='failed'
out=Path(__file__).parent.parent/'output/ooru-meeting-audit/verification/preservation.json';out.write_text(json.dumps(result,indent=2,default=str));print(json.dumps({k:v for k,v in result.items() if k not in ['tables','failures']}));assert not result['failures'],'Historical values changed; inspect the private reconciliation report'
