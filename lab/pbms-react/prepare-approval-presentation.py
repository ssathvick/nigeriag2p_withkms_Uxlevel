import pathlib,json,xmlrpc.client,time
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
creds=json.loads(pathlib.Path('/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json').read_text());entry=creds['admin']
auth=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb',entry['login'],entry['password'],{})
def staff(m,method,args=None,kw=None):return xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object').execute_kw('pbmsdb',auth,entry['password'],m,method,args or [],kw or {})
print('identity',staff('g2p.beneficiary.list','nsipa_identity'))
print('options count',len(staff('g2p.program.definition','nsipa_options')['groups']))
name='NSIPA_PRESENTATION'
found=call('g2p.program.definition','search',[[['program_mnemonic','=',name]]])
if found:p=found[0]
else:p=staff('g2p.program.definition','create',[{'program_mnemonic':name,'description':'Programme to Disbursement Approval Flow presentation. Fictional households only.','program_status':'ACTIVE','target_registry':'household','nsipa_flow':True,'service_providers_required':False}])
for i in [1,2]:
 link='NSIPA-PRESENTATION-'+str(i)
 if not call('g2p.household.registry','search_count',[[['link_registry_id','=',link]]]):call('g2p.household.registry','create',[{'link_registry_id':link,'name':'Fictional Presentation Household '+str(i),'annual_income':120000,'size_total':4,'large_area_code':'PL'}])
b=call('g2p.benefit.codes','search',[[['benefit_mnemonic','=','NSIPA_PRESENTATION_CASH']]])
if b:benefit=b[0]
else:benefit=staff('g2p.benefit.codes','create',[{'benefit_mnemonic':'NSIPA_PRESENTATION_CASH','benefit_type':'CASH_DIGITAL','measurement_unit':'NGN','decimal_places':2}])
staff('g2p.program.definition','nsipa_configure',[[p],benefit,repr([('link_registry_id','like','NSIPA-PRESENTATION-')]),25000])
for k,role in [('admin','Programme Admin'),('payment','Payment'),('finance','Finance'),('audit','Audit'),('ceo','CEO')]:call('g2p.program.definition','nsipa_assign_role',[[p],creds[k]['uid'],role])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/presentation-program.json').write_text(json.dumps({'program_id':p,'benefit_id':benefit}))
print('Actual presentation programme configured by the restricted Programme Admin account:',p)
