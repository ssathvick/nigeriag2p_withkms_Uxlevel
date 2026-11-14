from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor,Json
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT section_ui_schema FROM g2p_register_sections WHERE section_id='hh_members'");s=q.fetchone()['section_ui_schema'];w=s['panels'][0]['widgets'][0];w['widget']='household-members';w['widget-type']='table';q.execute("UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id='hh_members'",(Json(s),))
 c.commit()
print('Configured stable native household member editor')
