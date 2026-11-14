import json
from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("select section_id,section_ui_schema from g2p_register_sections where section_id='hh_composition_headship'"); print(json.dumps(q.fetchone(),default=str))
