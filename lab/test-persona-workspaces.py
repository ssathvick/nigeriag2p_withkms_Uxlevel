"""Isolated authorization and state-transition tests; no live records or integrations touched."""
import tempfile,os,json,sys,shutil,time,unittest
from pathlib import Path
temp=tempfile.TemporaryDirectory();root=Path(temp.name)
(root/'config.json').write_text(json.dumps({'base_url':'https://example.invalid','keycloak':'https://identity.invalid','clients':{}}))
shutil.copytree(Path(__file__).parent/'registration-ui',root/'templates');(root/'static').mkdir()
os.environ['IQS_REGISTRATION_ROOT']=str(root)
import registration_app as r
r.app.config['TESTING']=True
class Permissions(unittest.TestCase):
 def setUp(self):
  r.execute('DELETE FROM profiles');r.execute('DELETE FROM audit');r.execute('DELETE FROM sessions')
  data={'household_name':'Fictional household','state_name':'Kano','state':'NG01','community':'Dala','monthly_income':2000,'members':[{'given':'Fictional','family':'Person','birth_date':'1990-01-01','gender':'Female'}]}
  for sub in ['owner','other']:r.execute("INSERT INTO profiles(sub,household_ref,data,status,sync_status,updated) VALUES(?,?,?,'rejected','not_started','v1')",(sub,'HH-'+sub,json.dumps(data)))
  self.client=r.app.test_client();self.login('staff','officer',['iqs-registration-officer'])
 def login(self,mode,sub,roles):
  r.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',('testsession',json.dumps({'csrf':'test-csrf','mode':mode,'user':{'sub':sub,'name':'Test','roles':roles}}),int(time.time())+300));self.client.set_cookie('IQS-INTAKE','testsession')
 def post(self,action,**extra):return self.client.post('/registration/api/workspace/profile/owner/'+action,data={'csrf':'test-csrf','version':'v1',**extra})
 def test_anonymous_api_denied(self):
  self.client.delete_cookie('IQS-INTAKE');self.assertEqual(self.client.get('/registration/api/workspace').status_code,401)
 def test_default_login_destination_respects_staff_role(self):
  for role in ['iqs-registration-officer','iqs-verification-officer','iqs-programme-supervisor']:
   self.assertEqual(r.default_login_destination('staff',[role]),'/registration/analytics')
  self.assertEqual(r.default_login_destination('staff',['iqs-intake-reviewer']),'/registration/analytics')
  self.assertEqual(r.default_login_destination('staff',[]),'/registration/workspace')
  self.assertEqual(r.default_login_destination('beneficiary',[]),'/registration/analytics?service=beneficiary')
  self.assertEqual(self.client.get('/registration/staff').status_code,403)
 def test_citizen_ownership(self):
  self.login('beneficiary','owner',[]);d=self.client.get('/registration/api/workspace').json;self.assertEqual([p['sub'] for p in d['profiles']],['owner']);self.assertEqual(self.post('correct').status_code,403)
 def test_supervisor_read_only(self):
  self.login('staff','supervisor',['iqs-programme-supervisor']);self.assertEqual(self.client.get('/registration/api/workspace').json['personas'],['supervisor']);self.assertEqual(self.post('correct').status_code,403);self.assertEqual(self.post('approve').status_code,403)
 def test_csrf_denied(self):self.assertEqual(self.client.post('/registration/api/workspace/profile/owner/correct',data={'version':'v1'}).status_code,403)
 def test_version_conflict(self):self.assertEqual(self.post('correct',version='old').status_code,409)
 def test_invalid_income(self):self.assertEqual(self.post('correct',household_name='HH',community='Area',income='nan').status_code,400)
 def test_officer_and_independent_review(self):
  self.assertEqual(self.post('correct',household_name='Updated household',community='Updated community',income='35000').status_code,200)
  p=r.one('SELECT * FROM profiles WHERE sub=?',('owner',));self.assertEqual(p['status'],'pending_review')
  self.login('staff','officer',['iqs-intake-reviewer']);self.assertEqual(self.post('approve',version=p['updated'],checks='confirmed').status_code,403)
  self.assertEqual(self.client.post('/registration/staff/profile/owner/approve',data={'csrf':'test-csrf'}).status_code,403)
  self.login('staff','independent',['iqs-verification-officer']);original=r.sync_profile;r.sync_profile=lambda sub:r.execute("UPDATE profiles SET sync_status='complete' WHERE sub=?",(sub,))
  try:
   self.assertEqual(self.post('approve',version=p['updated']).status_code,400)
   self.assertEqual(self.post('approve',version=p['updated'],checks='confirmed').status_code,200)
   self.assertEqual(r.one('SELECT * FROM profiles WHERE sub=?',('owner',))['sync_status'],'complete')
   self.assertEqual(self.post('approve',version=p['updated'],checks='confirmed').status_code,409)
  finally:r.sync_profile=original
 def test_clear_return_reason(self):
  r.execute("UPDATE profiles SET status='pending_review' WHERE sub='owner'");self.login('staff','independent',['iqs-verification-officer'])
  self.assertEqual(self.post('reject',reason='short').status_code,400);self.assertEqual(self.post('reject',reason='Please confirm the community.').status_code,200)
  history=r.one("SELECT actor,action,reason FROM profile_reviews WHERE sub='owner' ORDER BY id DESC LIMIT 1")
  self.assertEqual(history['actor'],'independent');self.assertEqual(history['reason'],'Please confirm the community.')
if __name__=='__main__':unittest.main()
