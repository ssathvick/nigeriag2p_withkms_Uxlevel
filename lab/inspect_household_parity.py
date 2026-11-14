import json
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
out=Path(__file__).parent/'household-parity';out.mkdir(exist_ok=True)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("select * from g2p_register_sections where section_register_id in ('a0000000-0000-4000-8000-000000000002','a0000000-0000-4000-8000-000000000001')");rows=q.fetchall();(out/'sections-before.json').write_text(json.dumps(rows,default=str,indent=2))
  q.execute("select table_name,column_name,data_type from information_schema.columns where table_name like 'g2p_%' and (table_name like '%household%' or table_name like '%individual%' or table_name like '%intake_form%')");(out/'columns-before.json').write_text(json.dumps(q.fetchall(),default=str,indent=2))
  q.execute("select table_name,column_name,data_type from information_schema.columns where table_name like 'g2p_intake_form%' and table_name not like '%household%' and table_name not like '%individual%'");print(json.dumps(q.fetchall(),default=str)[:2500])
print('Captured metadata and column definitions')
