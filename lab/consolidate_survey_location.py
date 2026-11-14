from test_mbr_db_connection import connect
from psycopg2.extras import Json,RealDictCursor
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT section_id,section_ui_schema FROM g2p_register_sections WHERE section_id in ('hh_survey_consent','hh_location_details','hh_members')");rows={r['section_id']:r['section_ui_schema'] for r in q.fetchall()}
  def allw(x):
   if isinstance(x,dict):return ([x] if 'widget-id' in x else [])+sum([allw(v) for v in x.values()],[])
   if isinstance(x,list):return sum([allw(v) for v in x],[])
   return []
  widgets=rows['hh_survey_consent']['panels'][0]['widgets'];ids={w['widget-id'] for w in widgets}
  for w in allw(rows['hh_location_details']):
   if w['widget-id'] not in ids:widgets.append(w)
  q.execute("UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id='hh_survey_consent'",(Json(rows['hh_survey_consent']),))
  q.execute("DELETE FROM g2p_intake_form_ui_tab_sections WHERE tab_id='form_tab_household_intake' AND section_id='hh_location_details'")
  table=rows['hh_members']['panels'][0]['widgets'][0];table['widget-data-dialog-title-add']='Add Household Member';table['widget-data-dialog-title-edit']='Edit Household Member'
  for w in table['widget-data-columns']:
   if w['column-key']=='nin_id_type':w.pop('widget-data-options',None)
  q.execute("UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id='hh_members'",(Json(rows['hh_members']),))
 c.commit()
print('Consolidated location fields and member dialog labels')
