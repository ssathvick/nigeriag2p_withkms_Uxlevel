"""Exercise real OIDC signup and public forms with synthetic data only."""
import sys,os,time,json,secrets,pathlib,requests,yaml
from bs4 import BeautifulSoup
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
ROOT=r.ROOT;BASE=r.BASE;URL=BASE+'/registration';results={}
def csrf(response):return BeautifulSoup(response.text,'html.parser').select_one('input[name=csrf]')['value']
def auth(session,mode,username,password,signup=False):
 page=session.get(URL+'/login'+('?signup=1' if signup else '?mode='+mode),timeout=30);page.raise_for_status()
 form=BeautifulSoup(page.text,'html.parser').select_one('form')
 if not form:raise AssertionError('Expected identity form; '+str(page.status_code))
 data={f.get('name'):f.get('value','') for f in form.select('input[name]')};data.update({'username':username,'password':password})
 if signup:data.update({'email':username+'@example.invalid','firstName':'Amina','lastName':'IntegrationDemo','password-confirm':password})
 response=session.post(form['action'],data=data,timeout=40);response.raise_for_status()
 assert '/registration/' in response.url and 'keycloak.' not in response.url,('OIDC callback did not complete',response.status_code,BeautifulSoup(response.text,'html.parser').get_text(' ',strip=True)[-450:])
 return response
private=ROOT/'test-account.json'
if private.exists():account=json.loads(private.read_text());signup=False
else:account={'username':'iqs-registration-test-'+secrets.token_hex(3),'password':secrets.token_urlsafe(18)};private.write_text(json.dumps(account));os.chmod(private,0o600);signup=True
b=requests.Session();page=auth(b,'beneficiary',account['username'],account['password'],signup);results['public_oidc_signup_and_login']='passed'
assert b.get(URL+'/staff',timeout=30).status_code==403;results['beneficiary_cannot_review']='passed'
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];s=requests.Session();staff=auth(s,'staff','admin',password);assert 'Review, connect, enroll.' in staff.text;results['staff_oidc_login']='passed'
profile=b.get(URL+'/profile',timeout=30);assert profile.status_code==200
if 'This registration is approved.' not in profile.text:
 data={'csrf':csrf(profile),'household_name':'IQS Integration Test Household','state':'NG25','community':'Fictional Test Community','income':'30000','synthetic':'on','given_0':'Amina','family_0':'IntegrationDemo','birth_0':'1985-01-15','gender_0':'Female','given_1':'Musa','family_1':'IntegrationDemo','birth_1':'2014-06-12','gender_1':'Male'}
 with r.pg('master_data') as c:
  with c.cursor() as cur:cur.execute("SELECT level_value_id FROM g2p_geo_level_values WHERE length(level_value_id)=4 AND lower(level_value_mnemonic) LIKE '%lagos%' LIMIT 1");data['state']=cur.fetchone()[0]
 invalid=dict(data);invalid.pop('csrf');assert b.post(URL+'/profile',data=invalid,timeout=30).status_code==403;results['csrf_enforced']='passed'
 response=b.post(URL+'/profile',data=data,timeout=30);assert response.status_code==200 and 'Pending Review' in response.text
staff=s.get(URL+'/staff',timeout=30);p=r.one('SELECT * FROM profiles WHERE data LIKE ? ORDER BY updated DESC',('%'+account['username']+'@example.invalid%',));assert p
review=s.get(URL+'/staff/profile/'+p['sub'],timeout=30)
if p['status']!='approved':response=s.post(URL+'/staff/profile/'+p['sub']+'/approve',data={'csrf':csrf(review)},timeout=120);assert response.status_code==200
p=r.one('SELECT * FROM profiles WHERE sub=?',(p['sub'],));assert p['sync_status']=='complete',p['error'];results['household_and_people_synced_to_three_registries_and_pbms']='passed'
before=p['mapping'];r.sync_profile(p['sub']);assert before==r.one('SELECT mapping FROM profiles WHERE sub=?',(p['sub'],))['mapping'];results['registry_sync_idempotent']='passed'
pid=r.one('SELECT id FROM programs WHERE mnemonic=?',('IQS_INTEGRATED_HOUSEHOLD_SUPPORT',))['id'];home=b.get(URL+'/',timeout=30)
response=b.post(URL+'/apply/'+str(pid),data={'csrf':csrf(home)},timeout=60);assert response.status_code==200
response=b.post(URL+'/apply/'+str(pid),data={'csrf':csrf(response)},timeout=60);assert response.status_code==200
apps=r.rows('SELECT * FROM applications WHERE sub=? AND program=?',(p['sub'],pid));assert len(apps)==1;application=apps[0];results['repeated_application_is_single_record']='passed'
staff=s.get(URL+'/staff',timeout=30)
if application['status']=='pending_review':
 response=s.post(URL+'/staff/application/'+str(application['id'])+'/check',data={'csrf':csrf(staff)},timeout=120);assert response.status_code==200
print('OIDC signup, staff authorization, CSRF, registry sync and duplicate prevention passed. Awaiting native PBMS household eligibility.',flush=True)
for attempt in range(48):
 r.reconcile();application=r.one('SELECT * FROM applications WHERE id=?',(application['id'],))
 if application['status'] in ['eligible','enrolled']:break
 if application['error']:print('PBMS status:',application['error'],flush=True)
 time.sleep(5)
assert application['status'] in ['eligible','enrolled'],application;results['native_pbms_household_eligibility']='passed'
if application['status']=='eligible':
 staff=s.get(URL+'/staff',timeout=30);response=s.post(URL+'/staff/application/'+str(application['id'])+'/enroll',data={'csrf':csrf(staff)},timeout=60);assert response.status_code==200
application=r.one('SELECT * FROM applications WHERE id=?',(application['id'],));assert application['status']=='enrolled'
po=r.Odoo('portal-backend-odoo','portalpbmsdb');assert po.call('g2p.program_membership','read',[[application['portal_membership']]],{'fields':['state']})[0]['state']=='enrolled'
pb=r.Odoo('pbms-odoo','pbmsdb');listing=pb.call('g2p.beneficiary.list','read',[[application['pbms_list']]],{'fields':['list_workflow_status','eligibility_process_status','number_of_registrants']})[0];assert listing['list_workflow_status']=='approved_final_enrolment'
results['staff_final_enrollment_in_pbms_and_portal']='passed';results['test_household']=p['household_ref'];results['application_id']=application['id'];results['pbms_job_id']=application['pbms_list'];results['pbms_job']=listing
(ROOT/'test-results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
