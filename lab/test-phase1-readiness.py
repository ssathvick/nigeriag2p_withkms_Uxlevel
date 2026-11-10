import importlib.util,json,unittest,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('phase1_tests',Path(__file__).with_name('test-phase1-sandbox.py'));base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);r=base.r

class Readiness(base.Phase1):
 def test_readiness_requires_staff_and_reports_no_certificate(self):
  response=self.client.get('/registration/api/phase1/readiness');self.assertEqual(response.status_code,200)
  self.assertFalse(response.json['availability']['certified'])
  self.login('beneficiary',[]);self.assertEqual(self.client.get('/registration/api/phase1/readiness').status_code,403)
  self.login(sub='officer',roles=['iqs-registration-officer']);self.assertEqual(self.client.get('/registration/phase1/readiness').status_code,403)
 def test_public_skip_link_has_keyboard_target(self):
  self.assertIn(b'<main id="content" tabindex="-1">',self.client.get('/registration/phase1/portal').data)
 def test_availability_duplicate_probes_do_not_cover_missing_minutes(self):
  import datetime as dt
  at=dt.datetime.now(dt.timezone.utc).replace(second=0,microsecond=0)
  with r.phase1_db() as c:
   c.execute('DELETE FROM health_samples')
   for minutes,seconds in [(3,10),(3,20),(1,10)]:c.execute('INSERT INTO health_samples(at,probe,status,elapsed_ms) VALUES(?,?,200,10)',((at-dt.timedelta(minutes=minutes)+dt.timedelta(seconds=seconds)).isoformat(),'public'))
  result=self.client.get('/registration/api/phase1/readiness').json['availability']
  self.assertEqual(result['distinct_sample_minutes'],2);self.assertLess(result['observed_availability_percent'],100);self.assertGreaterEqual(result['missing_or_failed_samples'],1)
  with r.phase1_db() as c:c.execute('DELETE FROM health_samples')
 def setUp(self):
  super().setUp()
  r.execute('DELETE FROM profiles')
  with r.phase1_db() as c:
   c.execute('DELETE FROM conditionality')
   c.execute("DELETE FROM cms_history WHERE actor NOT LIKE 'system:%'")
   c.execute("DELETE FROM cms_entries WHERE author NOT LIKE 'system:%'")
 def condition(self,attendance=80,**extra):
  return self.client.post('/registration/phase1/conditionality',data={'csrf':'test-csrf','household':'DEMO-HH-01','period':'2026-10','attendance':str(attendance),**extra})
 def condition_action(self,cid,action,version):return self.client.post('/registration/phase1/conditionality/'+cid+'/'+action,data={'csrf':'test-csrf','version':version})
 def test_conditionality_threshold_and_three_distinct_actors(self):
  for attendance,expected in [(79,'held'),(80,'released')]:
   with r.phase1_db() as c:c.execute('DELETE FROM conditionality')
   self.login(sub='maker',roles=['iqs-registration-officer']);self.assertEqual(self.condition(attendance).status_code,302)
   cid=self.client.get('/registration/api/phase1/conditionality').json['cases'][0]['id']
   self.login(sub='maker',roles=['iqs-intake-reviewer']);self.assertEqual(self.condition_action(cid,'verify',1).status_code,403)
   self.login(sub='verifier',roles=['iqs-verification-officer']);self.assertEqual(self.condition_action(cid,'verify',1).status_code,302)
   self.login(sub='verifier',roles=['iqs-intake-reviewer']);self.assertEqual(self.condition_action(cid,'hold',2).status_code,403)
   self.login(sub='maker',roles=['iqs-programme-supervisor']);self.assertEqual(self.condition_action(cid,'hold',2).status_code,403)
   self.login(sub='releaser',roles=['iqs-programme-supervisor'])
   if attendance==79:self.assertEqual(self.condition_action(cid,'release',2).status_code,409)
   self.assertEqual(self.condition_action(cid,'hold' if attendance==79 else 'release',2).status_code,302)
   self.assertEqual(self.client.get('/registration/api/phase1/conditionality').json['cases'][0]['status'],expected)
   self.assertEqual(self.condition_action(cid,'release',2).status_code,409)
 def test_conditionality_validation_roles_and_no_overwrite(self):
  for changes in [{'attendance':'101'},{'attendance':'-1'},{'period':'2026-13'},{'household':'REAL-HH-1'},{'csrf':'bad'}]:self.assertIn(self.condition(**changes).status_code,(400,403))
  self.assertEqual(self.condition().status_code,302);self.assertEqual(self.condition().status_code,302);self.assertEqual(self.condition(79).status_code,409)
  case=self.client.get('/registration/api/phase1/conditionality').json['cases'][0];self.assertNotIn('maker',case)
  self.login(sub='officer',roles=['iqs-registration-officer']);self.assertEqual(self.condition_action(case['id'],'verify',1).status_code,403)
  self.login('beneficiary',[]);self.assertEqual(self.client.get('/registration/phase1/conditionality').status_code,403)
 def test_conditionality_release_requires_verified_current_evidence(self):
  self.condition();cid=self.client.get('/registration/api/phase1/conditionality').json['cases'][0]['id']
  self.assertEqual(self.condition_action(cid,'release',1).status_code,409)
  self.login(sub='verifier',roles=['iqs-verification-officer']);self.assertEqual(self.condition_action(cid,'verify',99).status_code,409)
 def fields(self,**extra):
  data={'csrf':'test-csrf','kind':'news'}
  for lang in ('en','ha','yo','ig'):data[lang+'_title']='Test title '+lang;data[lang+'_body']='Fictional body content '+lang
  return {**data,**extra}
 def cms_action(self,eid,act,version=1):return self.client.post('/registration/phase1/cms/'+eid+'/'+act,data={'csrf':'test-csrf','version':version})
 def test_cms_independent_review_publish_version_and_archive(self):
  self.login(sub='writer',roles=['iqs-registration-officer']);response=self.client.post('/registration/phase1/cms/save',data=self.fields());self.assertEqual(response.status_code,302);eid=response.location.rsplit('/',1)[-1]
  self.assertNotIn(b'Test title',self.client.get('/registration/phase1/portal').data)
  self.assertEqual(self.cms_action(eid,'submit').status_code,302)
  self.login(sub='writer',roles=['iqs-intake-reviewer']);self.assertEqual(self.cms_action(eid,'review').status_code,403)
  self.login(sub='reviewer',roles=['iqs-verification-officer']);self.assertEqual(self.client.get('/registration/phase1/cms/'+eid).status_code,200);self.assertEqual(self.cms_action(eid,'review').status_code,302);self.assertEqual(self.cms_action(eid,'publish').status_code,403)
  self.login(sub='publisher');self.assertEqual(self.cms_action(eid,'publish').status_code,302)
  for lang in ('en','ha','yo','ig'):self.assertIn(('Test title '+lang).encode(),self.client.get('/registration/phase1/portal?lang='+lang).data)
  data=self.fields(id=eid,version=1,en_title='Changed title');self.assertEqual(self.client.post('/registration/phase1/cms/save',data=data).status_code,302)
  self.assertIn(b'Test title en',self.client.get('/registration/phase1/portal').data);self.assertNotIn(b'Changed title',self.client.get('/registration/phase1/portal').data)
  self.assertEqual(self.client.post('/registration/phase1/cms/save',data=data).status_code,409)
  self.assertEqual(self.cms_action(eid,'archive',2).status_code,302);self.assertNotIn(b'Test title',self.client.get('/registration/phase1/portal').data)
  with r.phase1_db() as c:self.assertGreater(c.execute('SELECT COUNT(*) FROM cms_history WHERE entry=?',(eid,)).fetchone()[0],4)
 def test_cms_validation_csrf_xss_and_roles(self):
  for changes in ({'en_title':''},{'ha_body':'short'},{'ig_title':'x'*161},{'csrf':'bad'}):self.assertIn(self.client.post('/registration/phase1/cms/save',data=self.fields(**changes)).status_code,(400,403))
  data=self.fields(en_title='<script>alert(1)</script>');res=self.client.post('/registration/phase1/cms/save',data=data);self.assertEqual(res.status_code,302);edit=self.client.get(res.location);self.assertNotIn(b'<script>alert(1)</script>',edit.data);self.assertIn(b'&lt;script&gt;',edit.data)
  self.login('beneficiary',[]);self.assertEqual(self.client.get('/registration/phase1/cms').status_code,403)
 def test_public_search_metadata_language_and_no_personal_data(self):
  for lang in ('en','ha','yo','ig'):
   html=self.client.get('/registration/phase1/portal?lang='+lang).data
   self.assertIn(('<html lang="'+lang+'">').encode(),html);self.assertIn(b'href="#content"',html)
   summary=self.client.get('/registration/api/phase1/public-data?lang='+lang).json
   self.assertTrue(summary['synthetic']);self.assertNotIn('households',summary);self.assertEqual(summary['demo_zones'],6)
  html=self.client.get('/registration/phase1/portal?q=Dala').data;self.assertIn(b'Dala',html);self.assertNotIn(b'Maiduguri',html)
 def test_citizen_case_ownership_and_tracking(self):
  for sub in ('owner','other'):r.execute('INSERT INTO profiles(sub,household_ref,data,status) VALUES(?,?,?,?)',(sub,'HH-'+sub,'{}','pending_review'))
  self.login('beneficiary',[],sub='owner')
  response,data=self.case(household='HH-owner');self.assertEqual(response.status_code,302)
  own=self.client.get('/registration/phase1/grievances');self.assertIn(b'HH-owner',own.data)
  self.assertEqual(self.case(household='HH-other')[0].status_code,403)
  self.assertEqual(self.case(household='HH-owner',channel='sms')[0].status_code,403)
  self.assertEqual(self.client.get('/registration/api/phase1/report').status_code,403)
  self.login('beneficiary',[],sub='other');self.assertNotIn(b'HH-owner',self.client.get('/registration/phase1/grievances').data)
 def test_security_headers_and_bounded_agent_listing(self):
  response=self.client.get('/registration/phase1/portal');self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy']);self.assertIn("object-src 'none'",response.headers['Content-Security-Policy'])
  with r.phase1_db() as c:c.executemany("INSERT INTO agents VALUES(?,?,'onboarded',1,?)",[('EXTRA-'+str(i),'DEMO-HH-01',r.stamp()) for i in range(250)])
  report=self.report();self.assertEqual(report['agent_total'],256);self.assertEqual(len(report['agents']),200)
  with r.phase1_db() as c:c.execute("DELETE FROM agents WHERE id LIKE 'EXTRA-%'")

if __name__=='__main__':unittest.main()
