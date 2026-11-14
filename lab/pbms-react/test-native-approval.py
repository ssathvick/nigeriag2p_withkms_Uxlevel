import pathlib,time,datetime,json,base64,secrets,xmlrpc.client
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
checks=[]
def ok(name):checks.append(name);print('PASS',name,flush=True)
def denied(fn,name):
 try:fn()
 except xmlrpc.client.Fault:ok(name);return
 raise AssertionError('Unexpectedly allowed: '+name)
refs={r['name']:r['res_id'] for r in call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['model','=','res.groups']]],{'fields':['name','res_id']})}
assert refs
stamp=str(int(time.time()));tag='NSIPA_UAT_'+stamp
# Only fictional registry entries are used by these isolated programmes.
reg=call('g2p.household.registry','create',[{'link_registry_id':tag+'_001','name':'Fictional NSIPA Approval Household','annual_income':120000,'size_total':4,'large_area_code':'PL'}])
benefit=call('g2p.benefit.codes','create',[{'benefit_mnemonic':tag+'_CASH','benefit_type':'CASH_DIGITAL','measurement_unit':'NGN','decimal_places':2}])
program=call('g2p.program.definition','create',[{'program_mnemonic':tag,'description':'Isolated approval-flow verification; fictional household only; no payments','target_registry':'household','program_status':'ACTIVE','nsipa_flow':True,'service_providers_required':False}])
domain=repr([('link_registry_id','=',tag+'_001')])
call('g2p.program.definition','nsipa_configure',[[program],benefit,domain,25000])
ok('native benefit mapping, eligibility, entitlement and three approval groups saved')
base_group=call('ir.model.data','search_read',[[['module','=','base'],['name','=','group_user']]],{'fields':['res_id']})[0]['res_id']
users={}
for role in ['Payment','Finance','Audit','CEO']:
 pw=secrets.token_urlsafe(24);login=tag.lower()+'.'+role.lower()+'@example.invalid'
 user=call('res.users','create',[{'name':'NSIPA UAT '+role,'login':login,'password':pw,'groups_id':[[6,0,[base_group]]]}])
 call('g2p.program.definition','nsipa_assign_role',[[program],user,role])
 u=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb',login,pw,{})
 def make(u,pw):
  def execute(m,method,args=None,kw=None):return xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object').execute_kw('pbmsdb',u,pw,m,method,args or [],kw or {})
  return execute
 users[role]={'id':user,'call':make(u,pw)}
today=datetime.date.today();start=today-datetime.timedelta(days=12);end=today-datetime.timedelta(days=2);ds=today;de=today.replace(day=28)
en=call('g2p.enrollment.cycle','create',[{'program_id':program,'cycle_number':1,'enrollment_start_date':str(start),'enrollment_end_date':str(end),'disbursement_start_date':str(ds),'disbursement_end_date':str(de)}])
el=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':en,'mnemonic':tag+'_ENR'}])
assert call('g2p.beneficiary.list','read',[[el]],{'fields':['nsipa_status']})[0]['nsipa_status']=='pending'
ok('enrolment list created in persistent Pending state')
# Trigger the scheduled action in the test; the live cron uses this same method.
cron=call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['name','=','process_lists']]],{'fields':['res_id']})[0]['res_id']
call('ir.cron','method_direct_trigger',[[cron]])
row=call('g2p.beneficiary.list','nsipa_details',[[el]])
assert row['list']['nsipa_status']=='complete' and len(row['lines'])==1,row
ok('real Registry criteria, Completed enrolment and automatic approval')
dc=call('g2p.disbursement.cycle','create',[{'program_id':program,'cycle_mnemonic':tag+'_MONTHLY','nsipa_enrollment_cycle_id':en,'disbursement_schedule_date':str(ds)}])
dl=call('g2p.beneficiary.list','create',[{'disbursement_cycle_id':dc,'mnemonic':tag+'_DISB'}])
call('ir.cron','method_direct_trigger',[[cron]])
row=call('g2p.beneficiary.list','nsipa_details',[[dl]]);assert row['list']['nsipa_total']==25000,row
ok('monthly disbursement, persistent entitlement and NOB calculated')
for role in users:
 who=users[role]['call']('g2p.program.definition','nsipa_workspace',[[program]])
 assert len(who['lists'])==2
ok('separate staff accounts see shared programme records')
denied(lambda:call('g2p.beneficiary.list','nsipa_export',[[dl]]),'export blocked before final approval')
denied(lambda:users['CEO']['call']('g2p.beneficiary.list','nsipa_submit',[[dl]]),'CEO cannot initiate Payment submission')
pay=users['Payment']['call'];fin=users['Finance']['call'];audit=users['Audit']['call'];ceo=users['CEO']['call']
pay('g2p.beneficiary.list','nsipa_submit',[[dl],'Review monthly list'])
denied(lambda:ceo('g2p.beneficiary.list','nsipa_decide',[[dl],'approve','Bypass attempt']),'CEO cannot approve before Finance')
fin('g2p.beneficiary.list','nsipa_decide',[[dl],'approve','Finance checked',base64.b64encode(b'Fictional supporting document').decode(),'finance-review.txt'])
audit('g2p.beneficiary.list','nsipa_decide',[[dl],'reject','Reduce entitlement for correction test'])
row=call('g2p.beneficiary.list','nsipa_details',[[dl]]);assert row['list']['nsipa_status']=='rejected'
line=row['lines'][0]['id']
call('g2p.beneficiary.list','nsipa_correct',[[dl],line,24000,True,'Corrected entitlement after Audit review'])
pay('g2p.beneficiary.list','nsipa_submit',[[dl],'Correction completed'])
denied(lambda:audit('g2p.beneficiary.list','nsipa_decide',[[dl],'approve','Skip attempt']),'resubmission restarts Finance review')
for method,role in [(fin,'Finance'),(audit,'Audit'),(ceo,'CEO')]:method('g2p.beneficiary.list','nsipa_decide',[[dl],'approve',role+' independently checked corrected list'])
row=call('g2p.beneficiary.list','nsipa_details',[[dl]]);assert row['list']['nsipa_status']=='verified' and row['list']['nsipa_revision']==2
ok('independent sequential approval, rejection, correction and revision history')
result=call('g2p.beneficiary.list','nsipa_export',[[dl]])
raw=base64.b64decode(result['data']);assert raw.startswith(bytes.fromhex('d0cf11e0a1b11ae1'))
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-approval.xls').write_bytes(raw)
ok('native binary XLS export after three approvals')
denied(lambda:fin('g2p.beneficiary.list','nsipa_export',[[dl]]),'approver cannot perform Programme Admin export')
denied(lambda:call('g2p.beneficiary.list','nsipa_correct',[[dl],line,1,True,'tamper']),'verified beneficiary list is immutable')
denied(lambda:call('g2p.beneficiary.list','write',[[dl],{'nsipa_status':'complete'}]),'direct RPC workflow tampering blocked')
assert not call('g2p.disbursement.cycle','read',[[dc]],{'fields':['approved_for_disbursement']})[0]['approved_for_disbursement']
ok('export-only final verification does not activate payment dispatch')
# Pause fixtures and remove temporary test-account access after checks.
for u in users.values():call('res.users','write',[[u['id']],{'active':False}])
call('g2p.program.definition','write',[[program],{'program_status':'PAUSED'}])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-approval-results.json').write_text(json.dumps({'status':'passed','checks':checks,'program_id':program,'enrollment_list_id':el,'disbursement_list_id':dl},indent=2))
print('ALL NATIVE APPROVAL TESTS PASSED')
