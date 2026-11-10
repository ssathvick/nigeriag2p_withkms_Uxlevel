"""Isolated access, publication and discovery regression checks."""
import importlib.util,json,unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('kt',Path(__file__).with_name('test-knowledge.py'));kt=importlib.util.module_from_spec(spec);spec.loader.exec_module(kt)
r=kt.r
import local_ai
class Readiness(kt.Knowledge):
 def publish_private(self):
  aid,f=self.create();f.update(id=aid,version=1,visibility='staff',audience='officer',title='RESTRICTED COORDINATE MANUAL',review_due='2027-01-01');self.assertEqual(self.client.post('/registration/knowledge/admin/save',data=f).status_code,302)
  self.action(aid,'submit',2);self.login('reviewer',['iqs-verification-officer']);self.action(aid,'review',2);self.login('publisher',['iqs-programme-supervisor']);self.assertEqual(self.action(aid,'publish',2).status_code,302);return aid
 def test_private_all_consumer_routes(self):
  aid=self.publish_private()
  for identity in [None,('citizen',[],'beneficiary'),('verifier',['iqs-verification-officer'],'staff')]:
   if identity:self.login(*identity)
   else:self.client.delete_cookie('IQS-INTAKE',path='/registration')
   for suffix in ['', '?include_roles=1','?q=RESTRICTED']:
    result=self.client.get('/registration/api/knowledge'+suffix);self.assertNotIn(aid,[a['id'] for a in result.json['articles']]);self.assertIn('no-store',result.headers['Cache-Control'])
   for route in [f'/knowledge/{aid}',f'/knowledge/{aid}/export']:
    self.assertEqual(self.client.get('/registration'+route).status_code,404)
   self.assertNotIn(b'RESTRICTED COORDINATE MANUAL',self.client.get('/registration/knowledge?q=RESTRICTED').data)
  self.login('officer',['iqs-registration-officer']);self.assertEqual(self.client.get(f'/registration/knowledge/{aid}').status_code,200);self.assertIn(b'RESTRICTED',self.client.get(f'/registration/knowledge/{aid}/export').data)
 def test_ai_private_retrieval(self):
  aid=self.publish_private();r.execute('DELETE FROM ai_usage');self.login('citizen',[],'beneficiary')
  with patch.object(local_ai,'generate',return_value={'answer':'Guidance','source_ids':[]}) as model:
   result=self.client.post('/registration/api/ai/chat',data={'csrf':'km-csrf','module':'geography','stage':'Service overview','audience':'all','question':'How do I capture coordinates?'})
   self.assertEqual(result.status_code,200);self.assertNotIn('RESTRICTED COORDINATE MANUAL',str(model.call_args));self.assertNotIn(aid,[a['id'] for a in result.json['sources']])
 def test_governance_validation_and_draft_access(self):
  aid,f=self.create();self.assertEqual(self.client.get(f'/registration/knowledge/{aid}').status_code,404)
  for values in [{'visibility':'unsafe'},{'review_due':'2026-02-30'}]:
   bad={**f,**values};self.assertEqual(self.client.post('/registration/knowledge/admin/save',data=bad).status_code,400)
 def test_discovery_bounds(self):
  for route in ['/registration/knowledge?q=household+registration','/registration/knowledge?page=2']:
   self.assertEqual(self.client.get(route).status_code,200)
  for page in ['abc','99999']:
   self.assertEqual(self.client.get('/registration/knowledge?page='+page).status_code,400)
  self.assertEqual(self.client.get('/registration/api/knowledge?q='+'x'*161).status_code,400)
if __name__=='__main__':unittest.main()
