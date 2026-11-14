from pathlib import Path
p=Path(__file__).parent/'client-concerns/odk_native_registry_mapping.py';s=p.read_text().replace('import datetime,math,uuid','import datetime,math,uuid,json\nfrom pathlib import Path')
s=s.replace("data.get('version')!=template.get('version')","data.get('version') not in [template.get('version'),'2026111201']")
anchor=" extra=[{'section_id':'hh_members'"
block=''' if data.get('version')=='2026111301':
  config=json.loads((Path(__file__).parent/'odk_survey_choices.json').read_text())
  def decode(path,raw):
   choices=config['choices'].get('/data/'+path)
   if choices:
    if raw not in choices:raise ValueError('Invalid survey dropdown selection: '+path)
    return choices[raw]
   return raw
  for field,path in config['paths'].items():
   relative=path.removeprefix('/data/')
   if relative.startswith('members/') or field in ['record_name','household_head_name']:continue
   raw=get(relative)
   if not raw:continue
   if field in ['shock_types','crops_grown']:value=[decode(relative,v) for v in raw.split()]
   elif config['fieldtypes'][field]=='int':value=int(raw)
   elif config['fieldtypes'][field]=='decimal':value=float(raw)
   else:value=decode(relative,raw)
   payload[field]=value
  for row,node in zip(members,data.findall('members')):
   for field,path in config['paths'].items():
    if not path.startswith('/data/members/'):continue
    raw=(node.findtext(field) or '').strip()
    if not raw:continue
    value=decode('members/'+field,raw)
    if config['fieldtypes'][field]=='int':value=int(value)
    if field=='chronic_illness_flag':value=str(value).lower() in ['yes','true','1']
    row[field]=value
  locations=json.loads((Path(__file__).parent/'nigeria_locations.json').read_text());crosswalk=json.loads((Path(__file__).parent/'mobile-geo-crosswalk.json').read_text())
  selected={k:get('geography/'+k+'_id') for k in ['state','lga','ward']};hierarchy=[{'level':'country','level_value_id':'NG','level_value_mnemonic':'Nigeria'}]
  parent=None
  for key,collection in [('state','states'),('lga','lgas'),('ward','wards')]:
   value=selected[key]
   if not value:
    if any(selected[k] for k in ['state','lga','ward'][['state','lga','ward'].index(key)+1:]):raise ValueError('Incomplete administrative location hierarchy')
    break
   place=next((x for x in locations[collection] if x['id']==value and (key=='state' or x['parent']==parent)),None)
   if not place:raise ValueError('Invalid Nigeria administrative location selection')
   native=value if key=='ward' else crosswalk[value]
   hierarchy.append({'level':key,'level_value_id':native,'level_value_mnemonic':place['name']});parent=value
  if len(hierarchy)>1:payload.update(geo_lowest_level_value_id=hierarchy[-1]['level_value_id'],geo_code_hierarchy_json={'hierarchy':hierarchy,'lowest_level_value_id':hierarchy[-1]['level_value_id']})
  if coords:
   payload.update(location_accuracy_m=values[3],location_capture_source='Collect device location',location_captured_at=get('household/location_captured_at') or None)
'''
if anchor not in s:raise RuntimeError('Mapper anchor absent')
s=s.replace(anchor,block+anchor);p.write_text(s);print('Prepared shared survey and mobile location mapping')
