import unittest,tempfile,json,sys
from pathlib import Path
from unittest.mock import patch
import odk_sync_worker as w
HERE=Path(__file__).parent
class FakeResponse:
 def __init__(self,content):self.content=content
class Client:
 def __init__(self,xml):self.xml=xml;self.calls=[];self.fail=False;self.awe=None
 def get(self,path):return FakeResponse(self.xml)
 def post(self,path,data):
  self.calls.append(path)
  if 'save_intake' in path:
   if self.fail:raise TimeoutError('Simulated lost create response')
   return {'submission_id':'sid'}
  if 'get_intake' in path:return {'awe_request_id':self.awe}
  return {}
class SyncTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=w.ROOT;w.ROOT=Path(self.tmp.name);self.c=w.db()
  self.xml=(HERE/'odk-verification/0-numeric-source.xml').read_bytes();self.definition=(HERE/'odk-verification/0-numeric-definition.xml').read_bytes();self.master=json.loads((HERE/'odk-verification/master-0.json').read_text());self.client=Client(self.xml)
  self.master['GEO_VALUES']=json.loads((HERE/'geography-reference.json').read_text())
  self.mapped=w.map_submission(self.xml,self.definition,self.master);self.instance=self.mapped['odk_instance_id'];self.entry={'instanceId':self.instance}
 def tearDown(self):self.c.close();w.ROOT=self.old;self.tmp.cleanup()
 def run_case(self,found=None):
  with patch.object(w,'native_row',return_value=found):w.process(self.client,self.c,'nsipa_household_mapping_check',self.definition,self.master,self.entry)
 def row(self):return dict(self.c.execute('SELECT * FROM imports').fetchone())
 def test_repeated_delivery_creates_and_finalizes_once(self):
  self.run_case();self.run_case();self.assertEqual(sum('save_intake' in x for x in self.client.calls),1);self.assertEqual(sum('finalize' in x for x in self.client.calls),1)
 def test_lost_response_never_blind_retries(self):
  self.client.fail=True
  with self.assertRaises(TimeoutError):self.run_case()
  self.run_case();self.assertEqual(self.row()['state'],'CREATE_UNCERTAIN');self.assertEqual(len(self.client.calls),1)
 def test_lost_response_reconciles_existing(self):
  self.client.fail=True
  with self.assertRaises(TimeoutError):self.run_case()
  self.run_case((self.mapped['payload'],{'submission_id':'recovered'}));self.assertEqual(self.row()['submission_id'],'recovered');self.assertEqual(self.row()['state'],'SUBMITTED');self.assertEqual(sum('save_intake' in x for x in self.client.calls),1)
 def test_source_change_held_without_overwrite(self):
  self.run_case();self.client.xml=self.xml.replace(b'Emeka',b'Changed');self.run_case();self.assertEqual(self.row()['state'],'SOURCE_CHANGED');self.assertEqual(sum('save_intake' in x for x in self.client.calls),1)
 def test_unknown_numeric_never_created(self):
  self.client.xml=self.xml.replace(b'<roof_material>2</roof_material>',b'<roof_material>999</roof_material>');self.run_case();self.assertEqual(self.row()['state'],'QUARANTINED');self.assertEqual(self.client.calls,[])
 def test_existing_review_never_resubmitted(self):
  self.client.awe='returned-or-pending-request';self.run_case((self.mapped['payload'],{'submission_id':'existing'}));self.assertFalse(any('save_intake' in x or 'finalize' in x for x in self.client.calls));self.assertEqual(self.row()['state'],'SUBMITTED')
 def test_excluded_test_is_not_imported_on_replay(self):
  self.client.xml=self.xml.replace(b'<roof_material>2</roof_material>',b'<roof_material>999</roof_material>');self.run_case()
  self.c.execute("UPDATE imports SET state='EXCLUDED_TEST'");self.c.commit();self.client.calls.clear();self.run_case()
  self.assertEqual(self.row()['state'],'EXCLUDED_TEST');self.assertEqual(self.client.calls,[])
 def test_changed_excluded_source_is_held_again(self):
  self.client.xml=self.xml.replace(b'<roof_material>2</roof_material>',b'<roof_material>999</roof_material>');self.run_case()
  self.c.execute("UPDATE imports SET state='EXCLUDED_TEST'");self.c.commit();self.client.calls.clear();self.client.xml+=b' ';self.run_case()
  self.assertEqual(self.row()['state'],'SOURCE_CHANGED');self.assertEqual(self.client.calls,[])
if __name__=='__main__':unittest.main(verbosity=2)
