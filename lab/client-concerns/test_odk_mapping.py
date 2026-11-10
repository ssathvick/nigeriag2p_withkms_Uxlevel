import copy,json,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from odk_household_mapping import map_submission,parse_xml,choices,code
HERE=Path(__file__).parent
class MappingTests(unittest.TestCase):
 def setUp(self):
  self.xml=(HERE/'odk-verification/0-numeric-source.xml').read_bytes()
  self.definition=(HERE/'odk-verification/0-numeric-definition.xml').read_bytes()
  self.master=json.loads((HERE/'odk-verification/master-0.json').read_text())
 def test_all_published_numeric_choices(self):
  count=0
  for field,attribute in [('roof_material','ROOF_MATERIAL'),('water_source_type','WATER_SOURCE_TYPE')]:
   opts=choices(parse_xml(self.definition),'/data/household/'+field)
   for raw,label in opts.items():
    with self.subTest(field=field,raw=raw):
     root=parse_xml(self.xml);root.find('household/'+field).text=raw
     result=map_submission(ET.tostring(root),self.definition,self.master)
     expected=next(x['value_code'] for x in self.master[attribute] if x['value_display']==label)
     self.assertEqual(result['payload'][field],expected);count+=1
  self.assertEqual(count,14)
 def test_unknown_numeric_rejected(self):
  for field in ['roof_material','water_source_type']:
   root=parse_xml(self.xml);root.find('household/'+field).text='999'
   with self.assertRaisesRegex(ValueError,'Unmapped'):map_submission(ET.tostring(root),self.definition,self.master)
 def test_ambiguous_master_rejected(self):
  with self.assertRaisesRegex(ValueError,'ambiguous'):code('2',{'2':'Corrugated iron'},[{'value_display':'Corrugated iron','value_code':'A'},{'value_display':'Corrugated iron','value_code':'B'}])
 def test_missing_optional_omitted(self):
  root=parse_xml(self.xml)
  for field in ['roof_material','water_source_type']:root.find('household/'+field).text=''
  result=map_submission(ET.tostring(root),self.definition,self.master)
  self.assertNotIn('roof_material',result['payload']);self.assertNotIn('water_source_type',result['payload'])
 def test_invalid_source_rejected(self):
  for path,value in [('visit/consent','no'),('review/review_confirmation','no'),('household/household_name',''),('household/household_head_name',''),('household/household_size','0'),('household/children','99'),('location/coordinates','999 1 0 10')]:
   with self.subTest(path=path):
    root=parse_xml(self.xml);root.find(path).text=value
    with self.assertRaises(ValueError):map_submission(ET.tostring(root),self.definition,self.master)
  root=parse_xml(self.xml);root.set('version','unknown')
  with self.assertRaises(ValueError):map_submission(ET.tostring(root),self.definition,self.master)
 def test_identical_master_lists_on_both_domains(self):
  self.assertEqual(self.master,json.loads((HERE/'odk-verification/master-1.json').read_text()))
if __name__=='__main__':unittest.main(verbosity=2)
