import json
from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as cur:
  cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%history%' OR table_name LIKE '%version%' OR table_name LIKE '%section%' OR table_name LIKE '%schema%' OR table_name LIKE '%definition%') ORDER BY 1")
  tables=[x['table_name'] for x in cur.fetchall()];print('tables',tables)
  for t in tables:
   if 'history' in t or 'version' in t or t in ['g2p_register_definitions','g2p_register_sections','g2p_register_schemas']:
    cur.execute('SELECT * FROM '+t+' LIMIT 1');print(t,json.dumps(cur.fetchall(),default=str))
  cur.execute('SELECT * FROM g2p_intake_form_households ORDER BY created_at LIMIT 1');print('household',json.dumps(cur.fetchone(),default=str))
with connect('awe') as c:
 with c.cursor(cursor_factory=RealDictCursor) as cur:
  cur.execute("SELECT * FROM approval_request WHERE artifact_type='registry.intake_form' AND status='rejected' LIMIT 1");r=cur.fetchone();print('orphan',json.dumps(r,default=str))
  cur.execute('SELECT * FROM approval_event WHERE request_id=%s ORDER BY created_at',(r['id'],));print('orphan events',json.dumps(cur.fetchall(),default=str))
