from test_mbr_db_connection import connect
with connect() as c:
 with c.cursor() as q:q.execute('select datname from pg_database where not datistemplate');print([r[0] for r in q.fetchall()])
