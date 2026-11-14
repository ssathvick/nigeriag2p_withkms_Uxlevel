import os,pathlib,json,time,datetime,xmlrpc.client
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react')
exec((root.parent/'inspect-pbms-react.py').read_text().split('models =')[0])
checks=[]
def ok(s):checks.append(s);print('PASS',s,flush=True)
def denied(fn,label):
 try:fn()
 except xmlrpc.client.Fault:ok(label);return
 raise AssertionError('Unexpected permission: '+label)
creds=json.loads(pathlib.Path(os.environ.get('PBMS_APPROVAL_ACCOUNTS_FILE','/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json')).read_text())
actors={}
for role in ['payment','finance','audit','ceo']:
 c=creds[role];u=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb',c['login'],c['password'],{})
 def make(u,pw):return lambda model,method,args=None,kw=None:xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object').execute_kw('pbmsdb',u,pw,model,method,args or [],kw or {})
 actors[role]=make(u,c['password'])
tag='NSIPA_PAYMENT_UAT_'+str(int(time.time()))
benefit=call('g2p.benefit.codes','search',[[['benefit_mnemonic','=','NG_LAB_CASH']]])[0]
primary=call('g2p.farmer.registry','search_read',[[['link_registry_id','=','NG-LAB-001']]],{'fields':['link_registry_id'],'limit':1})
if not primary:primary=call('g2p.farmer.registry','search_read',[[['link_registry_id','like','NG-LAB-']]],{'fields':['link_registry_id'],'order':'id','limit':1})
assert primary
other=call('g2p.farmer.registry','search_read',[[['link_registry_id','like','NG-LAB-'],['link_registry_id','!=',primary[0]['link_registry_id']]]],{'fields':['link_registry_id'],'order':'id','limit':1});assert other
records=primary+other
p=call('g2p.program.definition','create',[{'program_mnemonic':tag,'description':'Synthetic connected-payment verification, local Example Bank only','target_registry':'farmer','program_status':'ACTIVE','nsipa_flow':True,'service_providers_required':False}])
for role in actors:call('g2p.program.definition','nsipa_assign_role',[[p],creds[role]['uid'],role.title() if role!='ceo' else 'CEO'])
call('g2p.program.definition','nsipa_configure',[[p],benefit,repr([('link_registry_id','in',[r['link_registry_id'] for r in records])]),2])
today=datetime.datetime.now(datetime.timezone.utc).date();e=call('g2p.enrollment.cycle','create',[{'program_id':p,'cycle_number':1,'enrollment_start_date':str(today-datetime.timedelta(days=12)),'enrollment_end_date':str(today-datetime.timedelta(days=2)),'disbursement_start_date':str(today),'disbursement_end_date':str(today.replace(day=28))}])
el=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':e,'mnemonic':tag+'_ENROLL'}])
cron=call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['name','=','process_lists']]],{'fields':['res_id']})[0]['res_id'];call('ir.cron','method_direct_trigger',[[cron]])
dc=call('g2p.disbursement.cycle','create',[{'program_id':p,'nsipa_enrollment_cycle_id':e,'cycle_mnemonic':tag+'_PAY','disbursement_schedule_date':str(today)}])
dl=call('g2p.beneficiary.list','create',[{'disbursement_cycle_id':dc,'mnemonic':tag+'_LIST'}]);call('ir.cron','method_direct_trigger',[[cron]])
d=call('g2p.beneficiary.list','nsipa_details',[[dl]]);assert len(d['lines'])==2
d['lines'].sort(key=lambda l:l['beneficiary_id']!=primary[0]['link_registry_id'])
call('g2p.beneficiary.list','nsipa_correct',[[dl],d['lines'][0]['id'],0.75,True,'Synthetic corrected amount must be preserved by payment'])
call('g2p.beneficiary.list','nsipa_correct',[[dl],d['lines'][1]['id'],1,False,'Synthetic excluded beneficiary must never be paid'])
opts=call('g2p.program.definition','nsipa_options',[]);route=next(r['id'] for r in opts['payment_routes'] if 'NG_LAB_FARMER' in r['label'])
call('g2p.beneficiary.list','nsipa_set_payment_route',[[dl],route])
denied(lambda:actors['payment']('g2p.beneficiary.list','nsipa_start_payment',[[dl]]),'payment blocked before approval')
denied(lambda:actors['payment']('g2p.beneficiary.list','nsipa_submit',[[dl],'Fraction test']),'fractional entitlements blocked before approval to prevent bridge truncation')
call('g2p.beneficiary.list','nsipa_correct',[[dl],d['lines'][0]['id'],1,True,'Whole NGN correction for installed bridge'])
actors['payment']('g2p.beneficiary.list','nsipa_submit',[[dl],'Synthetic payment UAT'])
for role in ['finance','audit']:
 actors[role]('g2p.beneficiary.list','nsipa_decide',[[dl],'approve',role+' approves corrected synthetic list'])
denied(lambda:actors['payment']('g2p.beneficiary.list','nsipa_start_payment',[[dl]]),'payment blocked before CEO approval')
actors['ceo']('g2p.beneficiary.list','nsipa_decide',[[dl],'approve','CEO approves exact synthetic list'])
denied(lambda:actors['ceo']('g2p.beneficiary.list','nsipa_start_payment',[[dl]]),'CEO cannot initiate payment')
denied(lambda:call('g2p.beneficiary.list','write',[[dl],{'nsipa_payment_hash':'tamper'}]),'direct payment-state changes blocked')
assert not call('g2p.disbursement.cycle','read',[[dc]],{'fields':['approved_for_disbursement']})[0]['approved_for_disbursement'];ok('CEO approval alone does not dispatch money')
# Leave final action to the actual Payment browser session.
result={'program_id':p,'list_id':dl,'tag':tag,'expected_beneficiary':d['lines'][0]['beneficiary_id'],'excluded_beneficiary':d['lines'][1]['beneficiary_id'],'expected_ngn':1,'checks':checks,'status':'ready for browser payment submission'}
(root/'evidence/connected-payments').mkdir(exist_ok=True)
(root/'evidence/connected-payments/fixture.json').write_text(json.dumps(result,indent=2));print('Synthetic approved payment fixture ready:',p,dl)
