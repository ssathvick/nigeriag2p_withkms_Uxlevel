import json,datetime
from pathlib import Path
from psycopg2.extras import RealDictCursor,Json
from test_mbr_db_connection import connect
root=Path(__file__).parent;data=json.loads((root/'field-app/android/assets/locations.json').read_text());mapping=json.loads((root/'household-parity/mobile-geo-crosswalk.json').read_text())
# Explicit spelling alias for the existing Kano LGA ID; no existing IDs or records are changed.
for l in data['lgas']:
 if l['name']=='Nasarawa' and mapping[l['parent']]=='NG19':mapping[l['id']]='NG1902'
assert len(mapping)==811
with connect('master_data') as c:
 with c.cursor() as q:
  q.execute("INSERT INTO g2p_geo_levels(level_id,level_mnemonic,parent_level_id) VALUES ('ward','Ward','lga') ON CONFLICT (level_id) DO NOTHING")
  for w in data['wards']:q.execute('INSERT INTO g2p_geo_level_values(level_value_id,level_id,level_value_mnemonic,parent_level_value_id) VALUES (%s,%s,%s,%s) ON CONFLICT (level_value_id) DO NOTHING',(w['id'],'ward',w['name'],mapping[w['parent']]))
 c.commit()
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT section_ui_schema FROM g2p_register_sections WHERE section_id='hh_location_details'");node=q.fetchone()['section_ui_schema']; geo=next(w for p in node['panels'] for p2 in p.get('panels',[p]) for w in p2.get('widgets',[]) if w.get('widget')=='geo-hierarchy')
  q.execute("SELECT section_ui_schema FROM g2p_register_sections WHERE section_id='hh_survey_consent'");schema=q.fetchone()['section_ui_schema'];widgets=schema['panels'][0]['widgets']
  if not any(w.get('widget')=='geo-hierarchy' for w in widgets):widgets.insert(5,geo)
  q.execute("UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id='hh_survey_consent'",(Json(schema),))
 c.commit()
(root/'household-parity/mobile-geo-crosswalk.json').write_text(json.dumps(mapping,indent=2));print(json.dumps({'statesFct':37,'lgas':774,'wardsAddedFromMobile':len(data['wards']),'existingGeoIdsPreserved':True}))
