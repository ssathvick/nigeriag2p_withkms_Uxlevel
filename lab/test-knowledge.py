"""Isolated knowledge lifecycle and access tests; no production writes."""
import unittest,importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('persona_tests',Path(__file__).with_name('test-persona-workspaces.py'));base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);r=base.r
class Knowledge(unittest.TestCase):
 def setUp(self):
  self.client=r.app.test_client();r.execute('DELETE FROM sessions');r.execute("DELETE FROM km_articles WHERE author NOT LIKE 'system:%'");self.login('author',['iqs-registration-officer'])
 def login(self,sub,roles,mode='staff'):
  import time
  r.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',('kmsession',json.dumps({'csrf':'km-csrf','mode':mode,'user':{'sub':sub,'name':'Test','roles':roles}}),int(time.time())+300));self.client.set_cookie('IQS-INTAKE','kmsession',path='/registration')
 def create(self):
  fields={'module':'geography','stage':'Test stage','audience':'all','title':'Test guidance','purpose':'Test purpose','steps':'One\nTwo','requirements':'Inputs','next_step':'Continue','issues':'Ask support','csrf':'km-csrf'}
  response=self.client.post('/registration/knowledge/admin/save',data=fields);self.assertEqual(response.status_code,302);return int(response.location.rsplit('/',1)[1]),fields
 def action(self,aid,act,version=1):return self.client.post(f'/registration/knowledge/admin/{aid}/{act}',data={'csrf':'km-csrf','version':version})
 def public(self,aid):return next((a for a in self.client.get('/registration/api/knowledge').json['articles'] if a['id']==aid),None)
 def test_public_and_private(self):
  self.client.delete_cookie('IQS-INTAKE',path='/registration');self.assertEqual(self.client.get('/registration/api/knowledge').status_code,200);self.assertEqual(self.client.get('/registration/knowledge/admin/new').status_code,401)
  self.login('citizen',[],'beneficiary');self.assertEqual(self.client.get('/registration/knowledge/admin').status_code,403)
 def test_lifecycle_version_and_archive(self):
  aid,fields=self.create();self.assertIsNone(self.public(aid));self.assertEqual(self.action(aid,'publish').status_code,403);self.assertEqual(self.action(aid,'submit').status_code,302)
  self.login('author',['iqs-intake-reviewer']);self.assertEqual(self.action(aid,'review').status_code,403)
  self.login('reviewer',['iqs-verification-officer']);self.assertEqual(self.action(aid,'review').status_code,302);self.assertEqual(self.action(aid,'publish').status_code,403)
  self.login('publisher',['iqs-programme-supervisor']);self.assertEqual(self.action(aid,'publish').status_code,302);self.assertEqual(self.public(aid)['version'],1)
  fields.update(id=aid,version=1,title='Revised guidance');self.assertEqual(self.client.post('/registration/knowledge/admin/save',data=fields).status_code,302);self.assertEqual(self.public(aid)['title'],'Test guidance');self.assertEqual(self.client.post('/registration/knowledge/admin/save',data=fields).status_code,409)
  self.assertEqual(self.action(aid,'archive',2).status_code,302);self.assertIsNone(self.public(aid));self.assertEqual(self.action(aid,'restore',2).status_code,302);self.assertIsNone(self.public(aid))
 def test_csrf_and_validation(self):
  aid,fields=self.create();self.assertEqual(self.client.post('/registration/knowledge/admin/'+str(aid)+'/submit',data={'version':1}).status_code,403);fields['module']='invalid';self.assertEqual(self.client.post('/registration/knowledge/admin/save',data=fields).status_code,400)
 def test_draft_escaped_and_history(self):
  aid,fields=self.create();fields.update(id=aid,version=1,title='<script>alert(1)</script>');self.client.post('/registration/knowledge/admin/save',data=fields);response=self.client.get('/registration/knowledge/admin/'+str(aid));self.assertEqual(response.status_code,200);self.assertNotIn(b'<script>alert(1)</script>',response.data);self.assertIn(b'&lt;script&gt;',response.data);self.assertTrue(r.rows('SELECT * FROM km_history WHERE article=?',(aid,)));hid=r.rows('SELECT id FROM km_history WHERE article=? ORDER BY id',(aid,))[0]['id'];self.assertEqual(self.client.get(f'/registration/knowledge/admin/{aid}/history/{hid}').status_code,200);self.assertEqual(self.client.post(f'/registration/knowledge/admin/{aid}/restore-version/{hid}',data={'csrf':'km-csrf','version':2}).status_code,302);self.assertEqual(r.one('SELECT version FROM km_articles WHERE id=?',(aid,))['version'],3)
 def test_independent_return_feedback(self):
  aid,fields=self.create();self.action(aid,'submit');self.login('reviewer',['iqs-verification-officer']);self.assertEqual(self.action(aid,'return').status_code,400);response=self.client.post(f'/registration/knowledge/admin/{aid}/return',data={'csrf':'km-csrf','version':1,'reason':'Clarify the required documents.'});self.assertEqual(response.status_code,302);a=r.one('SELECT * FROM km_articles WHERE id=?',(aid,));self.assertEqual(a['status'],'draft');self.assertIn('Clarify',a['review_note'])
 def test_documentation_sources_preserved_on_edit(self):
  a=r.one("SELECT * FROM km_articles WHERE author='system:documentation-import' LIMIT 1");self.assertIsNotNone(a)
  content=json.loads(a['draft']);self.assertTrue(content['sources']);self.assertEqual(content['scope'],'upstream_reference')
  data={k:content[k] for k in __import__('knowledge_management').FIELDS};data.update(id=a['id'],version=a['version'],csrf='km-csrf',title='Revised reference guidance')
  response=self.client.post('/registration/knowledge/admin/save',data=data);self.assertEqual(response.status_code,302)
  edited=r.one('SELECT * FROM km_articles WHERE id=?',(a['id'],));self.assertEqual(edited['status'],'draft');self.assertEqual(json.loads(edited['draft'])['sources'],content['sources']);self.assertEqual(json.loads(edited['published'])['title'],content['title']);r.execute('UPDATE km_articles SET draft=?,version=?,status=?,author=?,reviewer=? WHERE id=?',(a['draft'],a['version'],a['status'],a['author'],a['reviewer'],a['id']))
 def test_reference_links_and_public_coverage(self):
  from knowledge_management import reference_metadata,MODULES
  self.assertNotIn('sources',reference_metadata({'sources':[{'title':'Bad','url':'javascript:alert(1)'},{'title':'Bad','url':'https://evil.invalid/'}]}))
  articles=self.client.get('/registration/api/knowledge?include_roles=1').json['articles'];linked=[a for a in articles if a.get('sources')];self.assertEqual(len(linked),64);self.assertEqual({a['module'] for a in linked},set(MODULES));self.assertTrue(all(a['sources_checked_on']=='2026-10-05' for a in linked));self.assertIn(b'Upstream reference',self.client.get('/registration/knowledge').data)
 def test_search_role_filter_and_cors(self):
  response=self.client.get('/registration/api/knowledge?module=review&audience=citizen',headers={'Origin':'https://g2p-register.wverve.in'});self.assertEqual(response.headers['Access-Control-Allow-Origin'],'https://g2p-register.wverve.in');self.assertTrue(all(a['audience'] in ['all','citizen'] for a in response.json['articles']));self.assertNotIn('Access-Control-Allow-Origin',self.client.get('/registration/api/knowledge',headers={'Origin':'https://evil.invalid'}).headers);self.assertEqual(self.client.get('/registration/knowledge?q=household').status_code,200)
if __name__=='__main__':unittest.main()
