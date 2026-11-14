import sys,json,copy,uuid,xml.etree.ElementTree as E
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/odk-sync')
from odk_native_registry_mapping import map_native
from odk_household_mapping import parse_xml
root=Path(__file__).parent;definition=(root/'household-parity/nsipa_registry_household.xml').read_bytes();form=parse_xml(definition);data=copy.deepcopy(form.find('./head/model/instance/data'))
for n in data.iter():
 for key in list(n.attrib):
  if key.endswith('template'):del n.attrib[key]
def setv(path,value):
 n=data.find(path)
 if n is None:raise AssertionError(path)
 n.text=str(value)
values={'visit/sponsor_name':'NG_CARES','visit/consent_status':'YES','visit/respondent_name':'Fictional Offline Respondent','visit/enumerator_name':'SAMPLE_Amina_Bello_Kaduna','household/record_name':'Meeting Verification Offline Survey','household/household_head_name':'Fictional Offline Head','household/household_heads_count':1,'household/head_list_complete':'YES','household/coordinates':'9.0765 7.3986 0 12','household/location_captured_at':'2026-11-12T18:59:00Z','members/first_name':'Fictional','members/last_name':'Offline Head','members/gender':'MALE','members/estimated_age':40,'members/relationship_to_head':'SELF','members/nin_status':'NO','members/highest_education':'Senior_secondary','members/work_activity':'Fishing','living/income_source':'Fishing','living/monthly_household_income':'1000','living/health_insurance_status':'YES','income/major_shock_experienced':'YES','income/shock_types':'Flood Fire','possessions/owns_assets':'YES','possessions/owns_television':'YES','possessions/television_count':'2','crops/grows_crops':'YES','crops/crops_grown':'Maize Cassava','geography/state_id':'NG001','geography/lga_id':'NG001001','geography/ward_id':'NG001001_eziama','review/confirmation':'YES','meta/instanceID':'uuid:'+str(uuid.uuid4())}
choices=json.loads((root/'household-parity/odk_survey_choices.json').read_text())['choices'];values['visit/enumerator_name']=next(k for k,v in choices['/data/visit/enumerator_name'].items() if 'Amina Bello' in str(v))
for p,v in values.items():setv(p,v)
result=map_native(E.tostring(data),definition,{})
p=result['payload'];assert p['shock_types']==['Flood','Fire'] and p['crops_grown']==['Maize','Cassava'];assert p['location_accuracy_m']==12 and p['geo_lowest_level_value_id']=='NG001001_eziama';assert p['geo_code_hierarchy_json']['hierarchy'][1]['level_value_id']=='NG01';assert result['section_payloads'][0]['section_payload'][0]['highest_education']=='Senior secondary'
setv('geography/lga_id','NG002001')
try:map_native(E.tostring(data),definition,{});raise AssertionError('Invalid parent accepted')
except ValueError as e:assert 'location' in str(e)
(root.parent/'output/ooru-meeting-audit/verification/survey-offline-mapping.json').write_text(json.dumps({'status':'passed','formVersion':data.get('version'),'newFieldsPreserved':True,'gpsAccuracyAndTimestamp':True,'stateLgaWard':True,'invalidParentRejected':True},indent=2));print('PASS expanded offline survey mapping, GPS metadata and Nigeria hierarchy validation')
