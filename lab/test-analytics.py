"""Isolated analytics permissions, measurement and event integrity checks."""
import importlib.util,json,time,unittest,uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('base_tests',Path(__file__).with_name('test-persona-workspaces.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);r=base.r

class Analytics(unittest.TestCase):
 def setUp(self):
  self.client=r.app.test_client()
  for table in ['sessions','analytics_events','analytics_daily_usage','profiles','applications','audit','analytics_snapshots']:
   r.execute('DELETE FROM '+table)
  self.login('staff',['iqs-programme-supervisor'])
 def login(self,mode,roles):
  r.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',('analytics-test',json.dumps({'csrf':'test-csrf','mode':mode,'user':{'sub':'test','name':'Test','roles':roles}}),int(time.time())+300))
  self.client.set_cookie('IQS-INTAKE','analytics-test',path='/registration')
 def event(self,**extra):
  a=r.one("SELECT id,published_version FROM km_articles WHERE published IS NOT NULL AND status!='archived' LIMIT 1")
  data={'csrf':'test-csrf','event_id':str(uuid.uuid4()),'event_name':'guide_opened','article_id':str(a['id']),'version':str(a['published_version']),**extra}
  return self.client.post('/registration/api/analytics/events',data=data),data
 def test_permissions_and_no_pii(self):
  self.client.delete_cookie('IQS-INTAKE',path='/registration')
  self.assertEqual(self.client.get('/registration/api/analytics').status_code,401)
  self.login('beneficiary',[]);self.assertEqual(self.client.get('/registration/api/analytics').status_code,403)
  self.login('staff',[]);self.assertEqual(self.client.get('/registration/api/analytics').status_code,403)
  self.login('staff',['iqs-registration-officer']);self.assertEqual(self.client.get('/registration/api/analytics').status_code,200)
  self.assertEqual(self.client.get('/registration/api/analytics/export.csv').status_code,403)
 def test_live_revision_not_lost(self):
  a=r.one("SELECT * FROM km_articles WHERE published IS NOT NULL AND status!='archived' LIMIT 1")
  before=self.client.get('/registration/api/analytics').json['knowledge']['live']
  try:
   r.execute("UPDATE km_articles SET status='draft' WHERE id=?",(a['id'],))
   self.assertEqual(self.client.get('/registration/api/analytics').json['knowledge']['live'],before)
  finally:r.execute('UPDATE km_articles SET status=? WHERE id=?',(a['status'],a['id']))
 def test_restricted_service_sources(self):
  try:
   for source in ['Geographic record data','Staff access administration']:
    r.execute('INSERT OR REPLACE INTO analytics_source_cache VALUES(?,?,?,?,NULL)',(source,r.stamp(),'{"test":[{"label":"Count","value":7}]}',r.stamp()))
   self.login('staff',['iqs-registration-officer'])
   result=self.client.get('/registration/api/analytics').json
   self.assertNotIn('Geographic record data',[s['source'] for s in result['sources']])
   self.assertNotIn('iam-staff-ui',result['allowed_services'])
   self.assertEqual(self.client.get('/registration/api/analytics?service=iam-staff-ui').status_code,403)
   self.login('staff',['iqs-programme-supervisor'])
   self.assertEqual(self.client.get('/registration/api/analytics?service=iam-staff-ui').status_code,200)
  finally:r.execute("DELETE FROM analytics_source_cache WHERE source IN ('Geographic record data','Staff access administration')")
 def test_beneficiary_dashboard_ownership(self):
  for sub,count in [('test',2),('other',5)]:
   r.execute('INSERT INTO profiles(sub,data,status) VALUES(?,?,?)',(sub,'{}','approved' if sub=='test' else 'rejected'))
   for i in range(count):r.execute('INSERT INTO applications(sub,program,status,created) VALUES(?,?,?,?)',(sub,i,'enrolled' if sub=='test' else 'not_eligible',r.stamp()))
  self.login('beneficiary',[])
  response=self.client.get('/registration/api/analytics?service=beneficiary')
  self.assertEqual(response.status_code,200)
  data=response.json
  self.assertEqual(data['allowed_services'],['beneficiary']);self.assertEqual(len(data['sources']),1)
  self.assertEqual(data['sources'][0]['data']['my_application_status'],[{'label':'enrolled','value':2}])
  self.assertNotIn('not_eligible',json.dumps(data));self.assertNotIn('rejected',json.dumps(data))
  self.assertEqual(self.client.get('/registration/analytics?service=beneficiary').status_code,200)
  self.assertEqual(self.client.post('/registration/api/analytics/refresh',data={'csrf':'test-csrf'}).status_code,403)
 def test_refresh_requires_csrf_and_staff(self):
  self.assertEqual(self.client.post('/registration/api/analytics/refresh',data={'csrf':'wrong'}).status_code,403)
  self.login('staff',[])
  self.assertEqual(self.client.post('/registration/api/analytics/refresh',data={'csrf':'test-csrf'}).status_code,403)
 def test_demo_provenance_and_no_native_mix(self):
  try:
   r.execute("INSERT INTO dashboard_demo_records VALUES('TEST-DEMO','odk','submissions','Approved (demo)','Lagos',?,'test')",(r.stamp(),))
   data=self.client.get('/registration/api/analytics').json
   self.assertTrue(data['demo']['odk']['synthetic']);self.assertEqual(data['demo']['odk']['record_count'],1)
   self.assertEqual(data['demo']['odk']['data']['submissions'],[{'label':'Approved (demo)','value':1}])
   self.assertNotIn('TEST-DEMO',json.dumps(data['sources']))
  finally:r.execute("DELETE FROM dashboard_demo_records WHERE record_id='TEST-DEMO'")
 def test_dashboard_access_and_details(self):
  page=self.client.get('/registration/analytics?service=pbms')
  self.assertEqual(page.status_code,200);self.assertIn(b'dashboard-data',page.data)
  detail=self.client.get('/registration/analytics?view=details')
  self.assertEqual(detail.status_code,200);self.assertIn(b'Export aggregate CSV',detail.data)
  self.login('staff',[])
  self.assertEqual(self.client.get('/registration/analytics?service=pbms').status_code,403)
  self.login('beneficiary',[])
  self.assertEqual(self.client.get('/registration/analytics?service=register').status_code,403)
  self.client.delete_cookie('IQS-INTAKE',path='/registration')
  redirect=self.client.get('/registration/analytics?service=register')
  self.assertEqual(redirect.status_code,302);self.assertIn('service=register',redirect.location)
 def test_event_retry_csrf_and_versions(self):
  response,data=self.event();self.assertEqual(response.status_code,200);self.assertTrue(response.json['accepted'])
  self.assertFalse(self.client.post('/registration/api/analytics/events',data=data).json['accepted'])
  self.assertEqual(r.one('SELECT SUM(events) AS n FROM analytics_daily_usage')['n'],1)
  self.assertEqual(self.event(csrf='wrong')[0].status_code,403)
  self.assertEqual(self.event(version='999999')[0].status_code,409)
  self.assertEqual(self.event(event_id='bad')[0].status_code,400)
 def test_search_text_not_persisted_and_feedback(self):
  self.assertEqual(self.client.get('/registration/knowledge?q=SECRET-NIN-UNMATCHED').status_code,200)
  event=r.one("SELECT * FROM analytics_events WHERE event_name='search_completed'")
  self.assertEqual(event['result_count'],0);self.assertNotIn('SECRET',json.dumps(event))
  self.event(event_name='feedback_submitted',helpful='1')
  response,_=self.event(event_name='feedback_submitted',helpful='0');self.assertFalse(response.json['accepted'])
  k=self.client.get('/registration/api/analytics').json['knowledge'];self.assertEqual(k['zero_result_rate'],100);self.assertEqual(k['helpfulness'],100)
 def test_scope_snapshot_and_export(self):
  r.execute("INSERT INTO profiles(sub,data,status,sync_status,error) VALUES('PRIVATE-SUB',?,'pending_review','not_started','PRIVATE-ERROR')",(json.dumps({'state_name':'Kano','members':[{'given':'PRIVATE-NAME'}]}),))
  data=self.client.get('/registration/api/analytics').json
  self.assertEqual(data['operations']['review_backlog'],1);self.assertNotIn('PRIVATE',json.dumps(data))
  r.analytics_snapshot();self.assertEqual(len(self.client.get('/registration/api/analytics').json['snapshots']),1)
  response=self.client.get('/registration/api/analytics/export.csv');self.assertEqual(response.status_code,200);self.assertNotIn(b'PRIVATE',response.data)
  self.assertEqual(self.client.get('/registration/analytics').status_code,200)
  self.assertEqual(self.client.get('/registration/api/analytics?start=bad').status_code,400)
  self.assertEqual(self.client.get('/registration/api/analytics?module=bad').status_code,400)
 def test_review_episode_duration(self):
  a=r.one('SELECT id FROM km_articles LIMIT 1')['id'];today=r.stamp()[:10]
  h=[]
  try:
   for action,at in [('submit',today+'T01:00:00+00:00'),('return',today+'T03:00:00+00:00'),('submit',today+'T04:00:00+00:00'),('review',today+'T08:00:00+00:00')]:
    h.append(r.execute('INSERT INTO km_history(article,version,action,actor,at,content) VALUES(?,987,?,?,?,?)',(a,action,'test',at,'{}')))
   k=self.client.get('/registration/api/analytics').json['knowledge'];self.assertEqual(k['review_median_hours'],3);self.assertEqual(k['review_episodes'],2)
  finally:
   for hid in h:r.execute('DELETE FROM km_history WHERE id=?',(hid,))
 def test_programme_and_state_counts(self):
  pid=r.execute("INSERT INTO programs(mnemonic,name,amount) VALUES('ANALYTICS-TEST','Analytics test',0)")
  try:
   for sub,state in [('one','Kano'),('two','Lagos')]:
    r.execute("INSERT INTO profiles(sub,data,status) VALUES(?,?,'pending_review')",(sub,json.dumps({'state_name':state,'members':[]})))
    r.execute("INSERT INTO applications(sub,program,status,created) VALUES(?,?,'eligible',?)",(sub,pid,r.stamp()))
   d=self.client.get(f'/registration/api/analytics?programme={pid}&state=Kano').json
   self.assertEqual(d['operations']['profiles'],1);self.assertEqual(d['operations']['applications'],1)
   self.assertEqual(d['operations']['application_status'],[{'label':'eligible','count':1}])
  finally:
   r.execute('DELETE FROM applications WHERE program=?',(pid,));r.execute('DELETE FROM programs WHERE id=?',(pid,))
 def test_stale_source_and_usage_limit(self):
  import hashlib
  try:
   r.execute("INSERT OR REPLACE INTO analytics_source_cache VALUES('Test source','2000-01-01T00:00:00+00:00','{}',?,NULL)",(r.stamp(),))
   source=next(s for s in self.client.get('/registration/api/analytics').json['sources'] if s['source']=='Test source')
   self.assertTrue(source['stale']);self.assertFalse(source['error'])
   key=hashlib.sha256(b'analytics-test').hexdigest()
   for _ in range(120):r.execute("INSERT INTO analytics_events VALUES(?,'guide_opened',1,1,'platform',?,NULL,NULL,?)",(str(uuid.uuid4()),key,r.stamp()))
   self.assertEqual(self.event()[0].status_code,429)
   self.assertEqual(self.client.get('/registration/knowledge?q=household').status_code,200)
  finally:r.execute("DELETE FROM analytics_source_cache WHERE source='Test source'")
if __name__=='__main__':unittest.main()
