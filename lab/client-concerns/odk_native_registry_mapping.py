"""Map the full native offline form into native intake sections, without approval."""
import datetime,math,uuid,json
from pathlib import Path
from odk_household_mapping import parse_xml
REG='a0000000-0000-4000-8000-000000000002';IND='a0000000-0000-4000-8000-000000000001';ASSETS='b0000000-0000-4000-8000-000000000030'
def map_native(xml,definition,master):
 data=parse_xml(xml);form=parse_xml(definition);template=form.find('./head/model/instance/data')
 if data.get('id')!='nsipa_registry_household' or template is None or data.get('version') not in [template.get('version'),'2026111201','2026111301','2026111302','2026111303']:raise ValueError('Unapproved native form version')
 get=lambda path:(data.findtext(path) or '').strip()
 if get('visit/consent_status')!='YES' or get('review/confirmation')!='YES':raise ValueError('Consent and review confirmation required')
 instance=get('meta/instanceID');uuid.UUID(instance.removeprefix('uuid:'));internal=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+instance))
 payload={'internal_record_id':internal,'record_name':get('household/record_name'),'country_code':'NGA','address_line_1':get('household/address_line_1') or None}
 for field in ['sponsor_name','respondent_name','enumerator_name','consent_status','survey_community']:payload[field]=get('visit/'+field)
 if any(not payload.get(k) for k in ['record_name','sponsor_name','respondent_name','enumerator_name']):raise ValueError('Required native interview details missing')
 members=[]
 for i,node in enumerate(data.findall('members')):
  row={k:(node.findtext(k) or '').strip() for k in ['first_name','last_name','gender','birth_date','estimated_age','relationship_to_head','foundational_id']}
  if not row['first_name'] or not row['last_name'] or row['gender'] not in ['MALE','FEMALE','OTHER','UNKNOWN'] or row['relationship_to_head'] not in ['SELF','SPOUSE','CHILD','PARENT','SIBLING','OTHER_RELATIVE','NON_RELATIVE']:raise ValueError('Incomplete household member')
  if row['birth_date']:datetime.date.fromisoformat(row['birth_date'])
  elif not row['estimated_age']:raise ValueError('Member age or date of birth required')
  if row['estimated_age']:
   row['estimated_age']=int(row['estimated_age'])
   if not 0<=row['estimated_age']<=120:raise ValueError('Invalid member age')
  row={k:v for k,v in row.items() if v!=''};row.update(internal_record_id=str(uuid.uuid5(uuid.NAMESPACE_URL,internal+':member:'+str(i))),link_internal_record_id=internal,record_name=row['first_name']+' '+row['last_name'],full_name=row['first_name']+' '+row['last_name'],edit_action='ADD');members.append(row)
 heads=[m for m in members if m['relationship_to_head']=='SELF']
 if len(heads)!=1:raise ValueError('Exactly one household head is required')
 payload.update(registration_confirmed='YES',household_heads_count=1,head_list_complete='YES',size_total=len(members),household_head_name=heads[0]['record_name'],household_head_internal_record_id=heads[0]['internal_record_id'])
 for field in ['income_source','health_insurance_status','tenure_status']:
  value=get('living/'+field)
  if value:payload[field]=value
 for field in ['rooms_count','monthly_household_income']:
  raw=get('living/'+field)
  if raw:
   value=float(raw)
   if not math.isfinite(value) or value<0:raise ValueError('Invalid living-condition number')
   payload[field]=int(value) if field=='rooms_count' else value
 coords=get('household/coordinates')
 if coords:
  values=[float(v) for v in coords.split()]
  if len(values)!=4 or not all(math.isfinite(v) for v in values) or not -90<=values[0]<=90 or not -180<=values[1]<=180:raise ValueError('Invalid coordinates')
  payload.update(latitude=values[0],longitude=values[1],altitude=values[2])
 if data.get('version') in ['2026111301','2026111302','2026111303','2026111304']:
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
 extra=[{'section_id':'hh_members','section_register_id':IND,'section_payload':members}]
 assets=[]
 for i,node in enumerate(data.findall('assets')):
  kind=(node.findtext('asset_type') or '').strip()
  if not kind:continue
  if kind not in ['LAND','LIVESTOCK','PRODUCTIVE_TOOL','CONSUMER_DURABLE','VEHICLE','OTHER']:raise ValueError('Invalid asset type')
  row={'internal_record_id':str(uuid.uuid5(uuid.NAMESPACE_URL,internal+':asset:'+str(i))),'link_internal_record_id':internal,'asset_type':kind,'asset_category':node.findtext('asset_category') or None,'edit_action':'ADD'}
  if node.findtext('quantity'):
   row['quantity']=int(node.findtext('quantity'))
   if row['quantity']<0:raise ValueError('Invalid asset quantity')
  assets.append(row)
 if assets:extra.append({'section_id':'hh_table_assets','section_register_id':ASSETS,'section_payload':assets})
 return {'mapping_version':'2026-11-12.native','payload':payload,'section_payloads':extra,'odk_instance_id':instance,'form_id':data.get('id'),'form_version':data.get('version')}
