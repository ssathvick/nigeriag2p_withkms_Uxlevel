import json,os,re,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
scratch=tempfile.TemporaryDirectory()
os.environ['EXPERIENCE_DATABASE']=str(Path(scratch.name)/'bootstrap.sqlite')
os.environ['EXPERIENCE_GATEWAY_SECRET']='isolated-test-gateway'
os.environ['EXPERIENCE_SESSION_SECRET']='isolated-test-session'
os.environ['EXPERIENCE_SECURE_COOKIE']='0'
from app import create_app

class Experience(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  cfg=json.loads((ROOT/'config/deployment.json').read_text());cfg['allowed_origins']=['https://registry.example.invalid']
  self.cfg=Path(self.temp.name)/'config.json';self.cfg.write_text(json.dumps(cfg))
  self.app=create_app(self.cfg,Path(self.temp.name)/'knowledge.sqlite');self.app.testing=True;self.client=self.app.test_client()
  self.headers={}
 def tearDown(self):self.temp.cleanup()
 def login(self,sub,roles):self.headers={'X-Experience-Gateway':'isolated-test-gateway','X-Experience-Subject':sub,'X-Experience-Roles':','.join(roles)}
 def csrf(self):
  self.client.get('/experience/',headers=self.headers)
  with self.client.session_transaction(path='/experience/') as s:return s['csrf']
 def post(self,url,data):return self.client.post(url,data={'csrf':self.csrf(),**data},headers=self.headers)
 def draft(self):
  self.login('author',['knowledge-editor']);data=dict(module='intake',stage='Test intake',audience='all',title='Test guide',purpose='Purpose',steps='One\nTwo',requirements='Required',next_step='Next',issues='Support')
  res=self.post('/experience/knowledge/admin/save',data);self.assertEqual(res.status_code,302);return int(res.location.rsplit('/',1)[1]),data
 def action(self,aid,action,version=1):return self.post(f'/experience/knowledge/admin/{aid}/{action}',dict(version=str(version)))
 def published(self,aid):return next((a for a in self.client.get('/experience/api/knowledge').json['articles'] if a['id']==aid),None)
 def test_public_preview_and_assets(self):
  for route in ['/experience/','/experience/health','/experience/api/config','/experience/knowledge','/experience/static/help.js','/experience/static/workspace.js','/experience/embed/config.js']:
   response=self.client.get(route);self.assertEqual(response.status_code,200,route);response.close()
  self.assertEqual(len(self.client.get('/experience/api/knowledge').json['articles']),54)
 def test_untrusted_identity_is_rejected(self):
  self.headers={'X-Experience-Subject':'intruder','X-Experience-Roles':'knowledge-publisher'}
  self.assertEqual(self.client.get('/experience/knowledge/admin',headers=self.headers).status_code,401)
  self.headers['X-Experience-Gateway']='wrong';self.assertEqual(self.client.get('/experience/knowledge/admin',headers=self.headers).status_code,401)
 def test_role_enforcement(self):
  self.login('citizen',[]);self.assertEqual(self.client.get('/experience/knowledge/admin',headers=self.headers).status_code,403)
 def test_csrf(self):
  self.login('author',['knowledge-editor']);res=self.client.post('/experience/knowledge/admin/save',data={},headers=self.headers);self.assertEqual(res.status_code,403)
 def test_lifecycle_and_independence(self):
  aid,_=self.draft();self.assertIsNone(self.published(aid));self.assertEqual(self.action(aid,'submit').status_code,302)
  self.login('author',['knowledge-reviewer']);self.assertEqual(self.action(aid,'review').status_code,403)
  self.login('reviewer',['knowledge-reviewer']);self.assertEqual(self.action(aid,'review').status_code,302);self.assertEqual(self.action(aid,'publish').status_code,403)
  self.login('publisher',['knowledge-publisher']);self.assertEqual(self.action(aid,'publish').status_code,302);self.assertEqual(self.published(aid)['version'],1)
  self.assertEqual(self.action(aid,'archive').status_code,302);self.assertIsNone(self.published(aid));self.assertEqual(self.action(aid,'restore').status_code,302);self.assertIsNone(self.published(aid))
 def test_revision_conflict_and_snapshot(self):
  aid,data=self.draft();self.action(aid,'submit');self.login('reviewer',['knowledge-reviewer']);self.action(aid,'review');self.login('publisher',['knowledge-publisher']);self.action(aid,'publish')
  self.login('author',['knowledge-editor']);data.update(id=str(aid),version='1',title='Changed');self.assertEqual(self.post('/experience/knowledge/admin/save',data).status_code,302);self.assertEqual(self.published(aid)['title'],'Test guide');self.assertEqual(self.post('/experience/knowledge/admin/save',data).status_code,409)
 def test_html_escaped(self):
  aid,data=self.draft();data.update(id=str(aid),version='1',title='<script>alert(1)</script>');self.post('/experience/knowledge/admin/save',data)
  res=self.client.get(f'/experience/knowledge/admin/{aid}',headers=self.headers);self.assertIn(b'&lt;script&gt;',res.data);self.assertNotIn(b'<script>alert(1)</script>',res.data)
 def test_exact_origin_allowlist(self):
  res=self.client.get('/experience/api/knowledge',headers={'Origin':'https://registry.example.invalid'});self.assertEqual(res.headers.get('Access-Control-Allow-Origin'),'https://registry.example.invalid')
  res=self.client.get('/experience/api/knowledge',headers={'Origin':'https://registry.example.invalid.evil.test'});self.assertNotIn('Access-Control-Allow-Origin',res.headers)
 def test_no_business_tables(self):
  rows=self.app.extensions['experience_adapter'].rows("select name from sqlite_master where type='table'");self.assertEqual({r['name'] for r in rows},{'km_articles','km_history'})
 def test_bad_service_url(self):
  cfg=json.loads(self.cfg.read_text());cfg['services'][0]['url']='javascript:alert(1)';self.cfg.write_text(json.dumps(cfg))
  with self.assertRaises(ValueError):create_app(self.cfg,Path(self.temp.name)/'bad.sqlite')
 def test_content_validation(self):
  aid,data=self.draft();data['module']='invalid';self.assertEqual(self.post('/experience/knowledge/admin/save',data).status_code,400)
 def test_configured_stages_have_seed_content(self):
  stages={(a['module'],a['stage']) for a in self.client.get('/experience/api/knowledge').json['articles']}
  for rule in json.loads(self.cfg.read_text())['screen_mappings']:self.assertIn((rule['module'],rule['stage']),stages)

if __name__=='__main__':unittest.main(verbosity=2)
