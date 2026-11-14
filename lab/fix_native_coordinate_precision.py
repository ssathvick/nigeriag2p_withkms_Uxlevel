from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor,Json
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT section_id,section_ui_schema FROM g2p_register_sections WHERE register_id='a0000000-0000-4000-8000-000000000002'");rows=q.fetchall()
  def fix(v):
   if isinstance(v,dict):
    f=v.get('widget-id')
    if f in ['latitude','longitude','location_accuracy_m','monthly_household_income','altitude']:v['widget-data-format']={'numericType':'decimal','decimalPlaces':7 if f in ['latitude','longitude'] else 2,'allowSigned':f in ['latitude','longitude','altitude']}
    for x in v.values():fix(x)
   elif isinstance(v,list):
    for x in v:fix(x)
  for row in rows:fix(row['section_ui_schema']);q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id=%s',(Json(row['section_ui_schema']),row['section_id']))
 c.commit()
print('Preserved decimal precision for GPS and money fields')
