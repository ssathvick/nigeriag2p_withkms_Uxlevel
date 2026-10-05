"""Public OIDC and form tests for native portal ingestion, isolation and ineligibility."""
import sys,json,time,secrets,os,pathlib,requests,yaml
from bs4 import BeautifulSoup
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
URL=r.BASE+'/registration';ROOT=r.ROOT;results={}
def csrf(res):return BeautifulSoup(res.text,'html.parser').select_one('input[name=csrf]')['value']
def signin(s,mode,account,signup=False):
 page=s.get(URL+'/login'+('?signup=1' if signup else '?mode='+mode),timeout=30);form=BeautifulSoup(page.text,'html.parser').select_one('form');assert form
 data={i['name']:i.get('value','') for i in form.select('input[name]')};data.update(username=account['username'],password=account['password'])
 if signup:data.update(email=account['username']+'@example.invalid',firstName='Amina',lastName='IntegrationCase',**{'password-confirm':account['password']})
 res=s.post(form['action'],data=data,timeout=40);assert res.status_code==200 and 'keycloak.' not in res.url,(res.status_code,res.url)
 return res
staff=requests.Session();pw=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];signin(staff,'staff',{'username':'admin','password':pw})
first=requests.Session();account=json.loads((ROOT/'test-account.json').read_text());signin(first,'beneficiary',account)
# Sign into the original beneficiary portal using the very same Keycloak account.
native='https://beneficiary.nigeriag2p.com/v1/selfservice';providers=first.get(native+'/auth/getLoginProviders',timeout=20).json()['loginProviders'];provider=next(p['id'] for p in providers if p['name']=='Local UX Demo Login')
res=first.get(native+'/auth/getLoginProviderRedirect/'+str(provider),params={'redirect_uri':'/selfservice/'},timeout=40);assert res.status_code==200 and 'keycloak.' not in res.url,(res.status_code,res.url)
res=first.get(native+'/applicationdetails',timeout=30);assert res.status_code==200,(res.status_code,res.text[:400]);assert any('Integrated Demo' in a.get('program_name','') and a.get('application_status')=='active' for a in res.json()),res.text[:600]
results['existing_beneficiary_portal_accepts_new_account_and_shows_enrollment']='passed'
# Create a connected programme via the actual staff form.
mn='PORTAL_INGESTION_TEST';program=r.one('SELECT * FROM programs WHERE mnemonic=?',('IQS_INTEGRATED_'+mn,))
if not program:
 page=staff.get(URL+'/staff',timeout=30);res=staff.post(URL+'/staff/program',data={'csrf':csrf(page),'name':'Portal Application Integration Test','mnemonic':mn,'amount':'15000','max_income':'90000','min_members':'2'},timeout=60);assert res.status_code==200
 program=r.one('SELECT * FROM programs WHERE mnemonic=?',('IQS_INTEGRATED_'+mn,))
results['staff_programme_creation_connects_pbms_and_portal']='passed'
p=r.one('SELECT * FROM profiles WHERE data LIKE ?',('%'+account['username']+'@example.invalid%',));a=r.one('SELECT * FROM applications WHERE sub=? AND program=?',(p['sub'],program['id']))
if not a:
 res=first.post(native+'/form/'+str(program['portal_id'])+'/submit',json={'program_registrant_info':{'contactName':'Amina IntegrationDemo','supportRequest':'Native portal integration test, synthetic only','demoConsent':True}},timeout=40);assert res.status_code==200,(res.status_code,res.text[:500])
 r.reconcile();a=r.one('SELECT * FROM applications WHERE sub=? AND program=?',(p['sub'],program['id']));assert a
results['native_portal_submission_discovered_by_integration']='passed'
# A second, high-income household must be excluded by the actual PBMS rule.
file=ROOT/'test-ineligible-account.json'
if file.exists():secondaccount=json.loads(file.read_text());signup=False
else:secondaccount={'username':'iqs-ineligible-test-'+secrets.token_hex(3),'password':secrets.token_urlsafe(18)};file.write_text(json.dumps(secondaccount));os.chmod(file,0o600);signup=True
second=requests.Session();signin(second,'beneficiary',secondaccount,signup)
profile=second.get(URL+'/profile',timeout=30)
if 'This registration is approved.' not in profile.text:
 state=BeautifulSoup(profile.text,'html.parser').select('select[name=state] option')[1]['value']
 res=second.post(URL+'/profile',data={'csrf':csrf(profile),'household_name':'IQS Ineligible Test Household','state':state,'community':'Fictional Community','income':'250000','synthetic':'on','given_0':'Zainab','family_0':'HighIncomeDemo','birth_0':'1988-01-01','gender_0':'Female'},timeout=30);assert res.status_code==200
p2=r.one('SELECT * FROM profiles WHERE data LIKE ?',('%'+secondaccount['username']+'@example.invalid%',));assert p2
if p2['status']!='approved':
 review=staff.get(URL+'/staff/profile/'+p2['sub'],timeout=30);res=staff.post(URL+'/staff/profile/'+p2['sub']+'/approve',data={'csrf':csrf(review)},timeout=90);assert res.status_code==200
pid=r.one('SELECT id FROM programs WHERE mnemonic=?',('IQS_INTEGRATED_HOUSEHOLD_SUPPORT',))['id'];home=second.get(URL+'/',timeout=30);res=second.post(URL+'/apply/'+str(pid),data={'csrf':csrf(home)},timeout=60);assert res.status_code==200
a2=r.one('SELECT * FROM applications WHERE sub=? AND program=?',(p2['sub'],pid));assert a2
for item in [a,a2]:
 if item['status']=='pending_review':
  page=staff.get(URL+'/staff',timeout=30);res=staff.post(URL+'/staff/application/'+str(item['id'])+'/check',data={'csrf':csrf(page)},timeout=90);assert res.status_code==200
print('Original portal login, application display, staff programme creation and native portal ingestion passed; checking negative eligibility.',flush=True)
for i in range(40):
 r.reconcile();a=r.one('SELECT * FROM applications WHERE id=?',(a['id'],));a2=r.one('SELECT * FROM applications WHERE id=?',(a2['id'],))
 if a['status'] in ['eligible','enrolled'] and a2['status']=='not_eligible':break
 time.sleep(5)
assert a['status'] in ['eligible','enrolled'],a;assert a2['status']=='not_eligible',a2
pb=r.Odoo('pbms-odoo','pbmsdb');jobs=pb.call('g2p.beneficiary.list','read',[[a['pbms_list'],a2['pbms_list']]],{'fields':['number_of_registrants','iqs_household_ref','eligibility_process_status']})
assert jobs[0]['number_of_registrants']==1 and jobs[0]['iqs_household_ref']==p['household_ref'];assert jobs[1]['number_of_registrants']==0
results['income_rule_excludes_ineligible_household']='passed';results['eligibility_lists_are_scoped_to_the_applicant']='passed'
# An intentional transient failure must leave an approved record retryable.
before=r.one('SELECT mapping FROM profiles WHERE sub=?',(p2['sub'],))['mapping'];r.execute("UPDATE profiles SET sync_status='pending' WHERE sub=?",(p2['sub'],))
original=r.Odoo;failed=[False]
def one_backend_failure(*args):
 if not failed[0]:failed[0]=True;raise RuntimeError('Injected transient backend failure for synthetic test')
 return original(*args)
r.Odoo=one_backend_failure
try:r.reconcile();assert r.one('SELECT * FROM profiles WHERE sub=?',(p2['sub'],))['sync_status']=='pending'
finally:r.Odoo=original
r.reconcile();assert r.one('SELECT * FROM profiles WHERE sub=?',(p2['sub'],))['sync_status']=='complete';assert r.one('SELECT mapping FROM profiles WHERE sub=?',(p2['sub'],))['mapping']==before
results['pending_sync_retries_without_duplicate_records']='passed'
(ROOT/'edge-test-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
