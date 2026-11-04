import sys,json,unittest,tempfile,time
from pathlib import Path
from unittest.mock import patch,MagicMock
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
import registration_app as r
import jos_connected as j
class Controls(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.old=r.ROOT;r.ROOT=Path(self.temp.name)
  with r.db() as c:c.executescript('CREATE TABLE sessions(id TEXT PRIMARY KEY,data TEXT,expires INTEGER);CREATE TABLE jos_runs(id TEXT PRIMARY KEY,sub TEXT);CREATE TABLE profiles(sub TEXT,data TEXT);')
  self.client=r.app.test_client()
 def tearDown(self):r.ROOT=self.old;self.temp.cleanup()
 def session(self,staff=True):
  data={'csrf':'jos-test-csrf','mode':'staff' if staff else 'beneficiary','user':{'sub':'test-staff','name':'Test only','roles':['iqs-intake-reviewer'] if staff else []}}
  r.execute('INSERT INTO sessions VALUES(?,?,?)',('jos-test',json.dumps(data),int(time.time())+100));self.client.set_cookie('IQS-INTAKE','jos-test',path='/registration')
 def test_anonymous_read_denied(self):self.assertEqual(self.client.get('/registration/api/jos-cct').status_code,401)
 def test_beneficiary_read_denied(self):
  self.session(False);self.assertEqual(self.client.get('/registration/api/jos-cct').status_code,403)
 def test_csrf_blocks_write(self):
  self.session();self.assertEqual(self.client.post('/registration/jos-cct/JOS-NATIVE-001/dispatch').status_code,403)
 def test_nonstaff_write_denied(self):
  self.session(False);self.assertEqual(self.client.post('/registration/jos-cct/JOS-NATIVE-001/dispatch',data={'csrf':'jos-test-csrf'}).status_code,403)
 def test_unlisted_cohort_rejected(self):
  self.session();self.assertEqual(self.client.post('/registration/jos-cct/OTHER/dispatch',data={'csrf':'jos-test-csrf'}).status_code,409)
 def test_external_bank_guard(self):
  config={'spec':{'template':{'spec':{'containers':[{'env':[{'name':'G2P_BRIDGE_BANK_CONNECTORS_FUNDS_AVAILABLE_CHECK_URL_EXAMPLE_BANK','value':'https://external.invalid/check_funds'}]}]}}}}
  with patch.object(j.subprocess,'check_output',return_value=json.dumps(config)):
   with self.assertRaises(j.GuardError):j.routing_guard(r)
 def test_false_synthetic_claim_rejected(self):
  x={'sub':'jos-native:JOS-NATIVE-001','id':'JOS-NATIVE-001'};r.execute('INSERT INTO profiles VALUES(?,?)',(x['sub'],json.dumps({'synthetic':False,'jos_demo':x['id'],'household_name':'Real person'})))
  with self.assertRaises(j.GuardError):j.profile(r,x)
 def test_snapshot_is_allowlisted(self):
  row={k:None for k in ['id','name','household_ref','registry_status','modern_registry_id','program_id','cycle_id','list_id','application_status','condition','awe','dispatch_started','statement_requested','bank','bridge']};row['private_secret']='never publish'
  data={k:None for k in ['classification','checked_at','budget_usd','planning_households','connected_households','native_test_amount_ngn','exchange_rate_assumed','limitations']};data['rows']=[row]
  self.assertNotIn('private_secret',json.dumps(j.public_snapshot(data)))
 def test_minister_action_returns_to_same_sample_and_stage(self):
  self.session()
  with patch.object(j,'operate',return_value='Synthetic action accepted') as op:
   response=self.client.post('/registration/jos-cct/JOS-NATIVE-002/registry',data={'csrf':'jos-test-csrf','minister':'1','step':'1'})
   self.assertEqual(response.status_code,302)
   self.assertIn('/jos-cct/minister?sample=JOS-NATIVE-002&step=1',response.headers['Location'])
   op.assert_called_once_with(r,'JOS-NATIVE-002','registry','test-staff')
 def test_minister_guard_failure_stays_in_guide(self):
  self.session()
  with patch.object(j,'operate',side_effect=j.GuardError('Native eligibility is still processing')):
   response=self.client.post('/registration/jos-cct/JOS-NATIVE-002/enrol',data={'csrf':'jos-test-csrf','minister':'1','step':'2'})
   self.assertIn('step=2&error=1',response.headers['Location'])
 def test_minister_rejects_nonstaff(self):
  self.session(False);self.assertEqual(self.client.get('/registration/jos-cct/minister').status_code,403)
 def test_minister_rejects_unknown_sample(self):
  self.session();self.assertEqual(self.client.get('/registration/jos-cct/minister?sample=REAL').status_code,404)
 def test_minister_rejects_invalid_stage(self):
  self.session();self.assertEqual(self.client.get('/registration/jos-cct/minister?step=99').status_code,400)
if __name__=='__main__':unittest.main()
