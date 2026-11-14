import json
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
out=Path(__file__).parent.parent/'output/individual-workflow-verification';out.mkdir(exist_ok=True)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  result={}
  for table in ['g2p_intake_form_definitions','g2p_register_sections','g2p_register_ui_tabs','g2p_intake_form_ui_tabs','g2p_intake_form_ui_tab_sections']:
   q.execute('SELECT * FROM '+table);result[table]=[dict(r) for r in q.fetchall()]
  (out/'metadata.json').write_text(json.dumps(result,default=str,indent=2))
  for r in result['g2p_register_sections']:
   if str(r.get('section_register_id','')).endswith('001') or str(r.get('register_id','')).endswith('001'):print(r['section_id'],r.get('section_mnemonic'),json.dumps(r.get('section_ui_schema',{}))[:2500])
  print('FORMS',json.dumps(result['g2p_intake_form_definitions'],default=str)[:2200])
