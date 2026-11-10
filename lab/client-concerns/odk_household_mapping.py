"""Strict ODK XML -> existing household intake payload. No database writes."""
import hashlib,json,re,uuid,math,xml.etree.ElementTree as ET
from pathlib import Path

ALLOWED_FORMS={'nsipa_field_household_demo','nsipa_household_mapping_check'}
def parse_xml(data):
 if len(data)>2_000_000 or re.search(br'<!\s*(DOCTYPE|ENTITY)',data,re.I):raise ValueError('Unsupported XML declaration or size')
 node=ET.fromstring(data)
 for e in node.iter():e.tag=e.tag.rsplit('}',1)[-1]
 return node
def choices(form,path):
 field=next((e for e in form.iter('select1') if e.get('ref')==path),None)
 if field is None:return {}
 itemset=field.find('itemset')
 if itemset is not None:
  match=re.search(r"instance\(['\"]([^'\"]+)['\"]\)",itemset.get('nodeset',''))
  if not match:raise ValueError('Unsupported choice source')
  inst=next((e for e in form.iter('instance') if e.get('id')==match[1]),None)
  if inst is None:raise ValueError('Missing choice dictionary')
  return {e.findtext('name'):e.findtext('label') for e in inst.iter('item')}
 return {e.findtext('value'):e.findtext('label') for e in field.findall('item')}
def norm(value):return ' '.join(str(value).casefold().split())
def code(raw,options,master):
 if raw is None or not str(raw).strip():return None
 raw=str(raw).strip()
 if raw not in options:raise ValueError('Unmapped source choice: '+raw)
 label=options[raw]
 matches=[r for r in master if norm(r['value_display'])==norm(label)]
 if len(matches)!=1:raise ValueError('Missing or ambiguous master-data label: '+str(label))
 return matches[0]['value_code']
def map_submission(xml,definition,master):
 data=parse_xml(xml);form=parse_xml(definition);form_data=form.find('./head/model/instance/data')
 if form_data is None:raise ValueError('No primary XForm instance')
 if data.get('id') not in ALLOWED_FORMS or data.get('id')!=form_data.get('id') or data.get('version')!=form_data.get('version'):raise ValueError('Unapproved form or mismatched form version')
 get=lambda p:(data.findtext(p) or '').strip()
 if get('visit/consent')!='yes' or get('review/review_confirmation')!='yes':raise ValueError('Consent and local confirmation required')
 instance=get('meta/instanceID');uuid.UUID(instance.removeprefix('uuid:'))
 name=get('household/household_name');head=get('household/household_head_name')
 if not name or not head or len(name)>200 or len(head)>200:raise ValueError('Household and head names are required')
 size=int(get('household/household_size'));children=int(get('household/children'))
 if not 1<=size<=40 or not 0<=children<=size:raise ValueError('Invalid household counts')
 payload={'record_name':name,'household_head_name':head,'size_total':size,'country_code':'NGA','record_status':'ACTIVE','internal_record_id':str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-odk:'+data.get('id')+':'+instance))}
 places=[get('location/'+p) for p in ['ward','lga','state']]
 if not all(places):raise ValueError('Reported ward, LGA and state are required')
 payload['address_line_2']=', '.join(places)+' (reported ODK location)'
 coords=get('location/coordinates')
 if coords:
  values=[float(x) for x in coords.split()]
  if len(values)!=4 or not all(math.isfinite(v) for v in values) or not -90<=values[0]<=90 or not -180<=values[1]<=180 or not 0<=values[3]<100000:raise ValueError('Invalid geopoint')
  payload.update(latitude=values[0],longitude=values[1],altitude=values[2])
 for field,attribute in [('roof_material','ROOF_MATERIAL'),('water_source_type','WATER_SOURCE_TYPE')]:
  value=code(get('household/'+field),choices(form,'/data/household/'+field),master[attribute])
  if value is not None:payload[field]=value
 return {'mapping_version':'2026-11-10.1','form_id':data.get('id'),'form_version':data.get('version'),'odk_instance_id':instance,'source_sha256':hashlib.sha256(xml).hexdigest(),'payload':payload,'source_only':{'sample_reference':get('household/sample_reference'),'children_under_18':children,'shelter':get('household/shelter'),'livelihood_type':get('livelihood/livelihood_type'),'priority_needs':get('livelihood/priority_needs'),'gps_accuracy_m':coords.split()[3] if coords else None},'notes':['Reported area names are retained as reported text, not asserted as verified geographic IDs.','Children under 18 are not mapped to an under-five age bucket.','Source-only fields remain in this import receipt and the ODK source.']}
if __name__=='__main__':
 import sys
 xml,definition,master=map(Path,sys.argv[1:4]);print(json.dumps(map_submission(xml.read_bytes(),definition.read_bytes(),json.loads(master.read_text())),ensure_ascii=False))
