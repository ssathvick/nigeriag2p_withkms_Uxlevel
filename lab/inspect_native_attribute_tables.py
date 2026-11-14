import json
from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
with connect('master_data') as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("select table_name,column_name from information_schema.columns where table_name like '%attribute%value%'");print(json.dumps(q.fetchall()))
