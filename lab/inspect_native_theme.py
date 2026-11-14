from test_mbr_db_connection import connect
with connect() as c:
 with c.cursor() as q:
  q.execute("SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' AND (table_name LIKE '%theme%' OR table_name='g2p_registry_configurations') ORDER BY table_name,ordinal_position");print(q.fetchall())
  q.execute("SELECT theme_id,attribute_name,attribute_value FROM registry_theme_values WHERE attribute_name::text LIKE '%color%' ORDER BY theme_id,attribute_name");print(q.fetchall())
