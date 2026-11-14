from test_mbr_db_connection import connect
with connect() as c:
 with c.cursor() as q:q.execute('CREATE TABLE IF NOT EXISTS g2p_registry_review_comments(event_id text PRIMARY KEY,comment text NOT NULL)')
 c.commit()
print('Native approval comment store ready; original decisions remain unchanged.')
