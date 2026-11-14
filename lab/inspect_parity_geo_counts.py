from test_mbr_db_connection import connect
import json
with connect('master_data') as c:
 with c.cursor() as q:
  q.execute('SELECT level_id, count(*) FROM g2p_geo_level_values GROUP BY level_id');print(q.fetchall())
  q.execute("select * from g2p_geo_level_values where level_id='lga' limit 3");print(q.fetchall());q.execute('select * from g2p_geo_levels');print(q.fetchall())
