import json
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
report={}
for db in ['register','awe']:
 with connect(db) as c:
  with c.cursor(cursor_factory=RealDictCursor) as cur:
   cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
   tables=[x['table_name'] for x in cur.fetchall()]
   selected=[t for t in tables if (db=='awe' and any(k in t for k in ['approval','event','decision','outbox'])) or (db=='register' and any(k in t for k in ['intake','change_request','awe_req']))]
   data={}
   for table in selected:
    cur.execute('SELECT * FROM '+table+' LIMIT 3');samples=[dict(x) for x in cur.fetchall()]
    cur.execute('SELECT count(*) n FROM '+table);n=cur.fetchone()['n']
    cur.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position",(table,))
    data[table]={'count':n,'columns':cur.fetchall(),'samples':samples}
   report[db]=data
p=Path('/opt/openg2p-lab/registration/mbr-migration-inspection.json');p.write_text(json.dumps(report,default=str,indent=2));p.chmod(0o600)
for db,tables in report.items():
 print(db,json.dumps({k:v['count'] for k,v in tables.items()}))
 for t in (['approval_request','approval_task','approval_event','approval_decision'] if db=='awe' else ['g2p_intake_form_submissions','g2p_register_change_requests','g2p_register_change_request_payloads','g2p_intake_form_households','g2p_intake_form_individuals']):
  if t in tables:print(t,json.dumps(tables[t]['columns']))
