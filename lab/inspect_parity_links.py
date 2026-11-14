from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
import json
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  for t in ['g2p_intake_form_ui_tab_sections','g2p_register_ui_tab_sections','g2p_intake_form_ui_tabs','g2p_register_ui_tabs']:
   q.execute('SELECT * FROM '+t+' LIMIT 2');print(t,json.dumps(q.fetchall(),default=str))
  q.execute("SELECT * FROM g2p_intake_form_ui_tab_sections WHERE section_id in ('hh_composition_headship','hh_members','hh_dwelling_services','hh_assets')");print('hhlinks',json.dumps(q.fetchall(),default=str))
