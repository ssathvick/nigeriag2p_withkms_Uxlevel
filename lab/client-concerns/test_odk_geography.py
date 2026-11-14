import unittest,json,copy
from pathlib import Path
from odk_geography import resolve_geography
from odk_household_mapping import map_submission
HERE=Path(__file__).parent
class GeographyTests(unittest.TestCase):
 def setUp(self):self.values=json.loads((HERE/'geography-reference.json').read_text())
 def test_verified_hierarchy(self):
  result=resolve_geography(' Plateau ','JOS NORTH',self.values)
  self.assertEqual(result['geo_lowest_level_value_id'],'OCHA-NG032005')
  self.assertEqual([x['level_value_id'] for x in result['geo_code_hierarchy_json']['hierarchy']],['NG','NG31','OCHA-NG032005'])
 def test_lga_must_belong_to_state(self):
  with self.assertRaises(ValueError):resolve_geography('Lagos','Jos North',self.values)
 def test_unknown_location_not_guessed(self):
  with self.assertRaises(ValueError):resolve_geography('Plateau','Unknown',self.values)
 def test_duplicate_within_parent_rejected(self):
  self.values.append({**next(v for v in self.values if v['level_value_id']=='OCHA-NG032005'),'level_value_id':'DUP'})
  with self.assertRaises(ValueError):resolve_geography('Plateau','Jos North',self.values)
 def test_same_name_in_other_state_is_not_ambiguous(self):
  self.values.append({'level_id':'lga','level_value_id':'OTHER','parent_level_value_id':'NG24','level_value_mnemonic':'Jos North'})
  self.assertEqual(resolve_geography('Plateau','Jos North',self.values)['geo_lowest_level_value_id'],'OCHA-NG032005')
 def test_import_keeps_reported_ward_and_gps(self):
  master=json.loads((HERE/'odk-verification/master-0.json').read_text());master['GEO_VALUES']=self.values
  result=map_submission((HERE/'odk-verification/0-numeric-source.xml').read_bytes(),(HERE/'odk-verification/0-numeric-definition.xml').read_bytes(),master)
  self.assertEqual(result['payload']['geo_lowest_level_value_id'],'OCHA-NG032005')
  self.assertIn('Gangare',result['payload']['address_line_2'])
  self.assertEqual(result['payload']['latitude'],9.896527)
  self.assertNotIn('woreda_code',result['payload'])
if __name__=='__main__':unittest.main(verbosity=2)
