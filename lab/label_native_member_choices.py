from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor,Json
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT section_ui_schema FROM g2p_register_sections WHERE section_id='hh_members'");s=q.fetchone()['section_ui_schema']
  for col in s['panels'][0]['widgets'][0]['widget-data-columns']:
   for option in col.get('widget-data-source',{}).get('options',[]):
    if option.get('label')==option.get('value') and option['label']!='NIN' and option['label'].isupper():option['label']=option['label'].replace('_',' ').capitalize()
  q.execute("UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id='hh_members'",(Json(s),))
 c.commit()
print('Humanised member dropdown labels while preserving stored codes')
