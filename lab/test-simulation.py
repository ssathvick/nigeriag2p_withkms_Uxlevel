"""Isolated journey, authentication, callback and reset integrity tests."""
import importlib.util
import json
import shutil
import time
import unittest
import uuid
from pathlib import Path
spec=importlib.util.spec_from_file_location('base_tests',Path(__file__).with_name('test-persona-workspaces.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);r=base.r
shutil.copy2(Path(__file__).with_name('simulation-openapi.json'),r.ROOT/'simulation-openapi.json')

class Simulation(unittest.TestCase):
    def setUp(self):
        self.client=r.app.test_client()
        with r.simulation_db() as c:c.execute('DELETE FROM runs')
        self.login('staff',['iqs-programme-supervisor'])
    def login(self,mode,roles):
        r.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',('simulation-test',json.dumps({'csrf':'test-csrf','mode':mode,'user':{'sub':'test','name':'Test','roles':roles}}),int(time.time())+300))
        self.client.set_cookie('IQS-INTAKE','simulation-test',path='/registration')
    def start(self,scenario='success',key=None):
        return self.client.post('/registration/api/simulation/runs',data={'csrf':'test-csrf','scenario':scenario,'request_key':key or str(uuid.uuid4())})
    def finish(self):
        with r.simulation_db() as c:c.execute("UPDATE runs SET due_at='2000-01-01T00:00:00+00:00' WHERE due_at IS NOT NULL")
        r.simulation_tick()
    def test_roles_and_csrf(self):
        self.client.delete_cookie('IQS-INTAKE',path='/registration')
        self.assertEqual(self.client.get('/registration/api/simulation/report').status_code,401)
        self.login('beneficiary',[]);self.assertEqual(self.start().status_code,403)
        self.login('staff',['iqs-registration-officer']);self.assertEqual(self.start().status_code,403)
        self.login('staff',['iqs-intake-reviewer'])
        self.assertEqual(self.client.post('/registration/api/simulation/runs',data={}).status_code,403)
        self.assertEqual(self.start().status_code,200)
    def test_all_scenarios_and_settlement_amounts(self):
        expected={'success':'settled','identity_mismatch':'identity_rejected','ineligible':'social-register_rejected','invalid_account':'account_rejected','insufficient_funds':'treasury_rejected','payment_failed':'payment_failed','delayed_settlement':'settled','reconciliation_mismatch':'reconciliation_mismatch','reversal':'reversed'}
        for scenario in expected:self.assertEqual(self.start(scenario).status_code,200)
        self.finish()
        report=self.client.get('/registration/api/simulation/report').json
        self.assertEqual({x['scenario']:x['state'] for x in report['runs']},expected)
        self.assertEqual(report['settled_amount_minor'],5000000)
        self.assertEqual(report['counts']['settled'],2)
    def test_run_idempotency_and_conflicts(self):
        key=str(uuid.uuid4());first=self.start(key=key).json
        self.assertEqual(self.start(key=key).json,first)
        self.assertEqual(self.start('reversal',key).status_code,409)
        self.assertEqual(len(r.simulation_report()['runs']),1)
    def test_callback_duplicate_state_and_invalid_status(self):
        rid=self.start().json['run_id'];eid=str(uuid.uuid4())
        def send(status='successful',event=eid):
            return self.client.post('/registration/api/simulation/callback',data={'csrf':'test-csrf','run_id':rid,'event_id':event,'status':status})
        self.assertEqual(send('reversed').status_code,409)
        self.assertTrue(send().json['accepted']);self.assertFalse(send().json['accepted'])
        self.assertEqual(send('reversed').status_code,409)
        self.assertEqual(send(event=str(uuid.uuid4())).status_code,409)
        self.finish();self.assertEqual(r.simulation_report()['settled_amount_minor'],2500000)
    def test_delay_and_worker_retry(self):
        self.start('delayed_settlement');r.simulation_tick()
        self.assertEqual(r.simulation_report()['counts'],{'payment_accepted':1})
        self.finish();before=r.simulation_report();r.simulation_tick()
        self.assertEqual(before,r.simulation_report())
        with r.simulation_db() as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM callbacks').fetchone()[0],1)
    def test_isolation_reset_and_console(self):
        profiles=r.rows('SELECT * FROM profiles');applications=r.rows('SELECT * FROM applications')
        rid=self.start().json['run_id'];self.finish()
        self.assertEqual(self.client.get('/registration/simulation').status_code,200)
        self.assertEqual(self.client.get('/registration/simulation/run/'+rid).status_code,200)
        self.assertEqual(profiles,r.rows('SELECT * FROM profiles'));self.assertEqual(applications,r.rows('SELECT * FROM applications'))
        url='/registration/api/simulation/reset'
        self.assertEqual(self.client.post(url,data={'csrf':'test-csrf'}).status_code,400)
        self.assertEqual(self.client.post(url,data={'csrf':'test-csrf','confirmation':'RESET SYNTHETIC RUNS'}).status_code,302)
        with r.simulation_db() as c:
            self.assertEqual(c.execute('SELECT COUNT(*) FROM events').fetchone()[0],0)
            self.assertEqual(c.execute('SELECT COUNT(*) FROM callbacks').fetchone()[0],0)
    def test_partner_contracts_and_bad_inputs(self):
        contract=self.client.get('/registration/api/simulation/schema')
        self.assertEqual(contract.status_code,200)
        self.assertEqual(contract.json['openapi'],'3.1.0')
        for service in ['identity','social-register','programme','treasury','account','payment','notification','grievance','reconciliation']:
            result=self.client.post('/registration/api/simulation/partners/'+service,data={'csrf':'test-csrf','scenario':'success'})
            self.assertEqual(result.status_code,200);self.assertTrue(result.json['synthetic'])
            self.assertEqual(set(contract.json['components']['schemas'][service]['required']),set(result.json))
        self.assertEqual(self.start('unknown').status_code,400)
        self.assertEqual(self.start(key='bad').status_code,400)

if __name__=='__main__':unittest.main()
