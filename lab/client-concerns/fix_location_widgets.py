import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;reg='a0000000-0000-4000-8000-000000000002'
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute('SELECT section_ui_schema FROM g2p_register_sections WHERE register_id=%s AND section_id=%s FOR UPDATE',(reg,'hh_location_details'))
  schema=q.fetchone()[0];backup=root/'location-schema-before.json'
  if not backup.exists():backup.write_text(json.dumps(schema,indent=2))
  changes={'gps_latitude':('latitude','GPS Latitude'),'gps_longitude':('longitude','GPS Longitude'),'gps_accuracy':('altitude','Altitude (metres)'),'address_descriptor':('address_line_2','Reported location / address')}
  def walk(node):
   if isinstance(node,dict):
    old=node.get('widget-id')
    if old in changes:
     field,label=changes[old];node.update({'widget-id':field,'widget-label':label,'widget-data-path':reg+'.'+field})
     if field in ('latitude','longitude'):
      node['widget-data-format']['decimalPlaces']=6
      node['widget-data-validation']={'min':-90 if field=='latitude' else -180,'max':90 if field=='latitude' else 180}
     if field=='altitude':node['widget-data-placeholder']='Enter altitude in metres'
     if field=='address_line_2':node['widget-data-placeholder']='Enter reported location or address'
    for value in node.values():walk(value)
   elif isinstance(node,list):
    for value in node:walk(value)
  walk(schema)
  q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s::jsonb WHERE register_id=%s AND section_id=%s',(json.dumps(schema),reg,'hh_location_details'))
  (root/'location-schema-after.json').write_text(json.dumps(schema,indent=2))
print('Location widgets now bind to stored latitude, longitude, altitude and address_line_2. Accuracy remains source-only; no invented value.')
