import unittest,importlib.util,json
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('kt',Path(__file__).with_name('test-knowledge.py'));kt=importlib.util.module_from_spec(spec);spec.loader.exec_module(kt)
r=kt.r
import local_ai
class AI(kt.Knowledge):
 def setUp(self):
  super().setUp();r.execute('DELETE FROM ai_usage')
 def data(self):return {'csrf':'km-csrf','module':'geography','stage':'Service overview','audience':'all','question':'How do I capture household coordinates?','instructions':'Explain how staff capture household coordinates.'}
 def test_ai_auth_csrf_and_role(self):
  self.client.delete_cookie('IQS-INTAKE',path='/registration');self.assertEqual(self.client.post('/registration/api/ai/chat',data=self.data()).status_code,403)
  self.login('citizen',[],'beneficiary');self.assertEqual(self.client.post('/registration/api/ai/draft',data=self.data()).status_code,403)
  data=self.data();data.pop('csrf');self.assertEqual(self.client.post('/registration/api/ai/chat',data=data).status_code,403)
  data=self.data();data['audience']='supervisor';self.assertEqual(self.client.post('/registration/api/ai/chat',data=data).status_code,400)
 def test_ai_published_only_and_sources(self):
  aid,fields=self.create();fields['title']='PRIVATE DRAFT UNIQUE';fields.update(id=aid,version=1);self.client.post('/registration/knowledge/admin/save',data=fields)
  with patch.object(local_ai,'generate',return_value={'answer':'Use captured coordinates.','source_ids':[999999]}) as mock:
   response=self.client.post('/registration/api/ai/chat',data=self.data());self.assertEqual(response.status_code,200);self.assertNotIn('PRIVATE DRAFT UNIQUE',str(mock.call_args));self.assertEqual(response.json['source_label'],'Related published guidance');self.assertTrue(response.json['sources']);self.assertNotIn(999999,[a['id'] for a in response.json['sources']])
 def test_ai_draft_never_saves(self):
  before=[dict(a)for a in r.rows('SELECT * FROM km_articles')];draft={k:'Suggested '+k for k in local_ai.FIELDS}
  with patch.object(local_ai,'generate',return_value=draft):
   response=self.client.post('/registration/api/ai/draft',data=self.data());self.assertEqual(response.status_code,200);self.assertEqual(response.json['draft'],draft)
  self.assertEqual(before,[dict(a)for a in r.rows('SELECT * FROM km_articles')]);self.assertEqual(self.client.get('/registration/ai').status_code,200)
 def test_ai_limit_and_invalid_output(self):
  with patch.object(local_ai,'generate',return_value={'answer':'Answer','source_ids':[]}):
   for _ in range(8):self.assertEqual(self.client.post('/registration/api/ai/chat',data=self.data()).status_code,200)
   self.assertEqual(self.client.post('/registration/api/ai/chat',data=self.data()).status_code,429)
  r.execute('DELETE FROM ai_usage')
  with patch.object(local_ai,'generate',return_value={'title':'incomplete'}):self.assertEqual(self.client.post('/registration/api/ai/draft',data=self.data()).status_code,503)
if __name__=='__main__':unittest.main()

