"""Regression and acceptance cases for the five Swift governance actions."""
import io
import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('knowledge_tests',Path(__file__).with_name('test-knowledge.py'))
base=importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
r=base.r
import km_governance as gov
from knowledge_management import needs_authority

class ReviewTests(unittest.TestCase):
    login=base.Knowledge.login
    create=base.Knowledge.create
    action=base.Knowledge.action
    def setUp(self):
        base.Knowledge.setUp(self)
        with r.db() as c:
            for table in ('km_governance_events','km_change_targets','km_change_cases'):
                c.execute('DELETE FROM '+table)
        self.root='/registration/knowledge/admin'
    def reviewer(self,name='reviewer-1'):
        self.login(name,['iqs-verification-officer'])
    def pilot(self,slug):
        return r.one('SELECT * FROM km_articles WHERE slug=?',('context-'+slug,))
    def score(self,row,marks,kind='score',**changes):
        return self.client.post(f"{self.root}/{row['id']}/checks",data={'csrf':'km-csrf','kind':kind,'version':row['version'],
                'mark':marks,'note':'Synthetic calibration example',**changes})
    def test_rubric_all_levels_na_and_invalid(self):
        for level,rubric in gov.RUBRICS.items():
            self.assertEqual(sum(w for _,w in rubric),100)
            self.assertIsNone(gov.score_result(level,['NA']*4))
            self.assertEqual(gov.score_result(level,['NA','3','3','NA']),100)
            self.assertEqual(gov.score_result(level,['0']*4),0)
            with self.assertRaises(ValueError):gov.score_result(level,['4']*4)
        self.assertEqual(gov.score_result('field',['3','0','NA','NA']),41.7)
    def test_ten_blind_pairs_and_reconciliation(self):
        for slug in gov.CALIBRATION:
            row=self.pilot(slug); path=f"{self.root}/{row['id']}/checks"
            self.reviewer('calibration-A')
            self.assertEqual(self.score(row,['1','2','3','NA']).status_code,302)
            self.assertEqual(self.score(row,['3']*4).status_code,409)
            self.reviewer('calibration-B')
            self.assertNotIn(b'calibration-A',self.client.get(path).data)
            current=self.client.get(self.root+'/register?scope=calibration&export=json').json
            self.assertFalse(any(x['article']==row['id'] and x['kind']=='score' for x in current['records']))
            self.assertEqual(self.score(row,['3']*4,kind='reconcile').status_code,409)
            self.assertEqual(self.score(row,['3']*4).status_code,302)
            self.assertIn(b'calibration-A',self.client.get(path).data)
            self.assertEqual(self.score(row,[],kind='reconcile').status_code,302)
        out=self.client.get(self.root+'/register?scope=calibration&export=json').json
        self.assertEqual(len(out['articles']),10);self.assertEqual(len(out['records']),30)
    def test_preflight_catches_bad_draft_and_runs_at_transitions(self):
        aid,fields=self.create()
        with r.db() as c:
            for slug in ['first','second']:
                d={**fields,'title':'Revalidate','purpose':'Follow the approved procedure for eligibility.'}
                c.execute("INSERT INTO km_articles(slug,module,stage,audience,draft,version,status,author,updated) VALUES(?,?,?,?,?,1,'draft','author','now')",
                          (slug,'geography','Test','all',json.dumps(d)))
        a=r.one("SELECT * FROM km_articles WHERE slug='first'")
        page=self.client.get(f"{self.root}/{a['id']}/checks").data
        for flag in ('Source gap','Boilerplate','Duplicate wording','Terminology'):self.assertIn(flag.encode(),page)
        self.assertEqual(self.action(a['id'],'submit').status_code,302)
        self.reviewer(); self.assertEqual(self.action(a['id'],'review').status_code,302)
        self.login('publisher',['iqs-programme-supervisor'])
        self.assertEqual(self.action(a['id'],'publish').status_code,302)
        ev=r.rows("SELECT detail FROM km_governance_events WHERE article=? AND kind='preflight' ORDER BY id",(a['id'],))
        self.assertEqual([json.loads(x['detail'])['action'] for x in ev],['submit','publish'])
        self.assertTrue(all(len(json.loads(x['detail'])['issues'])==4 for x in ev))
    def test_selective_change_and_versioned_rereview(self):
        self.reviewer()
        payload={'csrf':'km-csrf','dependency':'pbms.approval-comment','description':'Mock proposal: Decision note replaces Approval comment.'}
        self.assertEqual(self.client.post(self.root+'/register/change',data=payload).status_code,302)
        cs=self.client.get(self.root+'/register?dependency=pbms.approval-comment&export=json').json
        self.assertEqual({a['level'] for a in cs['articles']},{'field','screen','workflow'})
        self.assertEqual(len(cs['articles']),5)
        change=cs['changes'][0]
        self.assertEqual({a['id'] for a in cs['articles']},{t['article'] for t in change['targets']})
        self.assertEqual(self.score(self.pilot('register-member-age'),[],kind='impact',change=change['id']).status_code,400)
        for a in cs['articles']:
            self.assertEqual(self.score(a,[],kind='impact',change=change['id']).status_code,302)
            old=dict(a,version=0)
            self.assertEqual(self.score(old,[],kind='impact',change=change['id']).status_code,409)
    def test_version_bound_report_upload_and_stale_rejection(self):
        row=self.pilot('pbms-finance')
        path=f"{self.root}/{row['id']}/checks"
        self.reviewer()
        snap=self.client.get(path+'/input').json
        units=snap['units']
        report={k:snap[k] for k in ('slug','version','digest')}
        report.update(model='Independent test fixture',prompt_version='1',prompt='Test review',at='fixture time',
                      instructional='Fixture',technical='Fixture',policy='Pending',verdict='Review required',
                      packet={'units':units,'sources':{'ref':{'reference':'Fixture source','text':'Example evidence'}}},
                      findings=[{'id':u['id'],'finding':'Fixture finding','status':'partial','sources':['ref']} for u in units])
        def post():
            return self.client.post(path+'/report',data={'version':row['version'],'csrf':'km-csrf',
                'report':(io.BytesIO(json.dumps(report).encode()),'check.json')}).status_code
        self.assertEqual(post(),302);self.assertEqual(post(),302)
        self.assertEqual(len(r.rows("SELECT id FROM km_governance_events WHERE kind='ai'")),1)
        self.assertIn(b'Independent test fixture',self.client.get(path).data)
        report['findings'].pop();self.assertEqual(post(),400)
        report['digest']='older';self.assertEqual(post(),400)
        self.login('citizen',[],'beneficiary')
        self.assertEqual(self.client.get(path+'/input').status_code,403)
    def test_near_duplicate_and_unrelated_negative(self):
        words='Inspect each reference and record the current date before submitting the verified file for independent review'
        item={'id':1,'draft':json.dumps({'module':'registry','purpose':words})}
        peers=[{'id':2,'draft':json.dumps({'module':'registry','purpose':words+' today'})},
               {'id':3,'draft':json.dumps({'module':'registry','purpose':'Choose your region'})}]
        flags=gov.preflight(item,peers,needs_authority)
        self.assertEqual([f[0] for f in flags],['Near-duplicate wording'])
        self.assertIn('2',flags[0][1]);self.assertNotIn('3',flags[0][1])
    def test_privacy_authorship_and_csrf(self):
        aid,fields=self.create()
        fields.update(id=aid,version=1,help_level='field',review_dependencies='private.policy.rev3')
        self.assertEqual(self.client.post(self.root+'/save',data=fields).status_code,302)
        self.reviewer('author');a=r.one('SELECT * FROM km_articles WHERE id=?',(aid,))
        self.assertEqual(self.score(a,['3']*4).status_code,403)
        self.reviewer()
        self.assertEqual(self.score(a,['3']*4,csrf='wrong').status_code,403)
        self.assertEqual(self.action(aid,'submit',2).status_code,302)
        self.assertEqual(self.action(aid,'review',2).status_code,302)
        self.login('publisher',['iqs-programme-supervisor'])
        self.assertEqual(self.action(aid,'publish',2).status_code,302)
        self.login('citizen',[],'beneficiary')
        for path in ('/register','/register?export=json',f'/{aid}/checks'):
            self.assertEqual(self.client.get(self.root+path).status_code,403)
        self.assertNotIn(b'private.policy.rev3',self.client.get('/registration/api/knowledge?include_roles=1').data)
        self.client.delete_cookie('IQS-INTAKE',path='/registration')
        self.assertEqual(self.client.get(self.root+'/register').status_code,401)

if __name__=='__main__':unittest.main()
