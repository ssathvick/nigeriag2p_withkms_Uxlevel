import unittest,json,hashlib,copy
from pathlib import Path
from odk_legacy_mapping import map_legacy
from odk_household_mapping import map_submission
ROOT=Path('/opt/openg2p-lab/odk-sync/legacy-review');WORK=Path(__file__).parent/'legacy-verification'
class LegacyTests(unittest.TestCase):
 def setUp(self):
  self.items=json.loads((WORK/'approved-mappings.json').read_text());self.master=json.loads((WORK/'master.json').read_text());self.review=self.items[0]['review'];self.xml=(ROOT/(self.review['instance_id'].replace(':','_')+'.xml')).read_bytes();self.definition=(ROOT/self.review['definition_file']).read_bytes()
 def test_all_five_preserve_original_and_counts(self):
  for item in self.items:
   review=item['review'];xml=(ROOT/(review['instance_id'].replace(':','_')+'.xml')).read_bytes();mapped=map_legacy(xml,self.definition,self.master,review)
   self.assertEqual(mapped['source_sha256'],hashlib.sha256(xml).hexdigest());self.assertEqual(mapped,item['mapping']);self.assertNotIn('latitude',mapped['payload']);self.assertNotIn('roof_material',mapped['payload']);self.assertIn('Synthetic ',mapped['payload']['record_name'])
 def test_changed_source_rejected(self):
  with self.assertRaisesRegex(ValueError,'source hash'):map_legacy(self.xml+b' ',self.definition,self.master,self.review)
 def test_changed_definition_rejected(self):
  with self.assertRaisesRegex(ValueError,'definition hash'):map_legacy(self.xml,self.definition+b' ',self.master,self.review)
 def test_no_authorization_rejected(self):
  review=copy.deepcopy(self.review);review['authorization']=''
  with self.assertRaisesRegex(ValueError,'not authorized'):map_legacy(self.xml,self.definition,self.master,review)
 def test_other_instance_rejected(self):
  review=copy.deepcopy(self.review);review['instance_id']='other'
  with self.assertRaisesRegex(ValueError,'instance mismatch'):map_legacy(self.xml,self.definition,self.master,review)
 def test_synthetic_label_required(self):
  review=copy.deepcopy(self.review);review['synthetic_names']['household_head_name']='Unlabelled Name'
  with self.assertRaisesRegex(ValueError,'label required'):map_legacy(self.xml,self.definition,self.master,review)
 def test_unenriched_source_still_fails_required_names(self):
  with self.assertRaisesRegex(ValueError,'names are required'):map_submission(self.xml,self.definition,self.master)
if __name__=='__main__':unittest.main(verbosity=2)
