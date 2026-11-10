"""Exercise sandbox transitions, durable queues, validation and access boundaries."""
import importlib.util
import json
import time
import unittest
import uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('base_tests',Path(__file__).with_name('test-persona-workspaces.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);r=base.r

class Phase1(unittest.TestCase):
    def setUp(self):
        self.client=r.app.test_client()
        with r.phase1_db() as c:
            for name in ('events','grievances','deliveries'): c.execute('DELETE FROM '+name)
            c.execute("UPDATE agents SET state='certified',version=1")
        self.login()
    def login(self,mode='staff',roles=None,sub='supervisor'):
        r.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',('phase1-test',json.dumps({'csrf':'test-csrf','mode':mode,'user':{'sub':sub,'name':'Test','roles':roles if roles is not None else ['iqs-programme-supervisor']}}),int(time.time())+3600))
        self.client.set_cookie('IQS-INTAKE','phase1-test',path='/registration')
    def case(self,**extra):
        data={'csrf':'test-csrf','request_id':str(uuid.uuid4()),'household':'DEMO-HH-01','channel':'web','reason':'payment_delay',**extra}
        return self.client.post('/registration/phase1/grievances',data=data),data
    def update(self,cid,action,version=1):
        return self.client.post('/registration/phase1/grievances/'+cid+'/'+action,data={'csrf':'test-csrf','version':version})
    def proof(self,**extra):
        data={'csrf':'test-csrf','id':str(uuid.uuid4()),'household':'DEMO-HH-01','biometric':'mock_match','latitude':'12','longitude':'8.5','accuracy_m':'5','captured':'2026-01-01T10:00:00.123Z',**extra}
        return self.client.post('/registration/api/phase1/deliveries',data=data),data
    def report(self): return self.client.get('/registration/api/phase1/report').json
    def test_permissions_csrf_and_public_portal(self):
        self.client.delete_cookie('IQS-INTAKE',path='/registration')
        self.assertEqual(self.client.get('/registration/api/phase1/report').status_code,401)
        self.assertEqual(self.client.get('/registration/phase1').status_code,302)
        for lang in ('en','ha','yo','ig'):
            res=self.client.get('/registration/phase1/portal?lang='+lang)
            self.assertEqual(res.status_code,200);self.assertIn(('lang="'+lang+'"').encode(),res.data)
        self.assertEqual(self.client.get('/registration/phase1/portal?lang=bad').status_code,400)
        for mode,roles in [('beneficiary',[]),('staff',['iqs-registration-officer']),('staff',[])]:
            self.login(mode,roles);self.assertEqual(self.client.get('/registration/phase1/field').status_code,403);self.assertEqual(self.case()[0].status_code,409 if mode=='beneficiary' else 403)
        self.login();self.assertEqual(self.case(csrf='bad')[0].status_code,403)
    def test_all_channels_and_idempotent_intake(self):
        for channel in ('web','mobile','sms','ussd','call_centre','physical_desk'):
            response,data=self.case(channel=channel);self.assertEqual(response.status_code,302)
            self.assertEqual(self.client.post('/registration/phase1/grievances',data=data).status_code,302)
        self.assertEqual(len(self.report()['grievances']),6)
        self.assertEqual(self.client.post('/registration/phase1/grievances',data={**data,'reason':'account_issue'}).status_code,409)
        for kwargs in ({'household':'PRIVATE-ID'},{'channel':'email'},{'reason':'unknown'},{'request_id':'bad'}):self.assertEqual(self.case(**kwargs)[0].status_code,400)
    def test_case_lifecycle_version_and_deadlines(self):
        self.case();case=self.report()['grievances'][0];cid=case['id']
        from datetime import datetime
        self.assertEqual((datetime.fromisoformat(case['response_due'])-datetime.fromisoformat(case['created'])).total_seconds(),48*3600)
        self.assertEqual((datetime.fromisoformat(case['resolution_due'])-datetime.fromisoformat(case['created'])).days,14)
        self.assertEqual(self.update(cid,'resolve').status_code,409)
        self.assertEqual(self.update(cid,'acknowledge').status_code,302)
        self.assertEqual(self.update(cid,'escalate',1).status_code,409)
        self.assertEqual(self.update(cid,'escalate',2).status_code,302)
        self.assertEqual(self.update(cid,'resolve',3).status_code,302)
        self.assertEqual(self.update(cid,'resolve',4).status_code,409)
        case=self.report()['grievances'][0];self.assertEqual(case['status'],'resolved');self.assertIsNotNone(case['responded']);self.assertIsNotNone(case['resolved'])
    def test_overdue_escalation_flags(self):
        self.case()
        with r.phase1_db() as c:c.execute("UPDATE grievances SET response_due='2000-01-01T00:00:00+00:00', resolution_due='2000-01-02T00:00:00+00:00'")
        case=self.report()['grievances'][0];self.assertTrue(case['response_overdue']);self.assertTrue(case['resolution_overdue'])
        self.assertEqual(case['status'],'escalated');r.phase1_tick()
        self.assertEqual(len([x for x in self.report()['events'] if x['action']=='grievance_auto_escalated']),1)
    def test_durable_delivery_and_duplicate_protection(self):
        response,data=self.proof();self.assertEqual(response.status_code,200);self.assertTrue(response.json['accepted'])
        retry=self.client.post('/registration/api/phase1/deliveries',data=data);self.assertEqual(retry.status_code,200);self.assertTrue(retry.json['duplicate'])
        self.assertEqual(self.proof()[0].status_code,409)
        self.assertEqual(self.client.post('/registration/api/phase1/deliveries',data={**data,'latitude':'13'}).status_code,409)
        self.login(sub='different');self.assertEqual(self.client.post('/registration/api/phase1/deliveries',data=data).status_code,409)
        self.assertEqual(len(self.report()['deliveries']),1)
        self.assertEqual(len([x for x in self.report()['events'] if x['action']=='delivery_synced']),1)
    def test_invalid_location_timestamp_and_biometric_denied(self):
        for changes in ({'accuracy_m':'11'},{'latitude':'nan'},{'longitude':'181'},{'biometric':'mock_mismatch'},{'captured':'2100-01-01T00:00:00+00:00'},{'captured':'2026-01-01T00:00:00'},{'household':'REAL-HH'}):
            with self.subTest(changes=changes):self.assertEqual(self.proof(**changes)[0].status_code,400)
        self.assertEqual(len(self.report()['deliveries']),0)
    def test_offline_shell_contains_no_session_secrets(self):
        response=self.client.get('/registration/phase1/field');self.assertEqual(response.status_code,200)
        self.assertNotIn(b'test-csrf',response.data);self.assertNotIn(b'phase1-test',response.data)
        self.assertEqual(self.client.get('/registration/phase1').status_code,200)
        self.assertEqual(self.client.get('/registration/api/phase1/context').json['csrf'],'test-csrf')
        import shutil
        shutil.copy2(Path(__file__).with_name('knowledge')/'phase1-sw.js',r.ROOT/'static/phase1-sw.js')
        worker=self.client.get('/registration/phase1/field/sw.js')
        self.assertEqual(worker.status_code,200)
        self.assertEqual(worker.headers['Service-Worker-Allowed'],'/registration/phase1/field')
        worker.close()
    def test_base_records_not_modified(self):
        before=r.rows('SELECT * FROM profiles');self.case();self.proof();self.assertEqual(before,r.rows('SELECT * FROM profiles'))
    def test_agent_lifecycle_and_delivery_gate(self):
        with r.phase1_db() as c:c.execute("UPDATE agents SET state='onboarded',version=1 WHERE id='DEMO-AGENT-01'")
        self.assertEqual(self.proof()[0].status_code,409)
        def action(name,version):return self.client.post('/registration/phase1/agents/DEMO-AGENT-01/'+name,data={'csrf':'test-csrf','version':version})
        self.assertEqual(action('certify',1).status_code,409)
        self.assertEqual(action('train',1).status_code,302)
        self.assertEqual(action('certify',1).status_code,409)
        self.assertEqual(action('certify',2).status_code,302)
        self.assertEqual(self.proof()[0].status_code,200)
        self.assertEqual(action('revoke',3).status_code,302)

if __name__=='__main__':unittest.main()
