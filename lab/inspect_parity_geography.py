from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
import json
with connect('master_data') as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("select table_name from information_schema.tables where table_name like '%geo%'");tables=q.fetchall();print(tables)
  for r in tables:
   if r['table_name'] in ['g2p_geo_levels','g2p_geo_level_values']:
    q.execute('select * from '+r['table_name']+' limit 3');print(r['table_name'],json.dumps(q.fetchall(),default=str))
