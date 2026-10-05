import subprocess,pathlib,yaml,xmlrpc.client
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
ip=subprocess.check_output(['kubectl','get','svc','pbms-odoo','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
uid=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb','admin@nigeria.openg2p.localhost',password,{})
m=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object')
def call(model,method,args,kw={}):return m.execute_kw('pbmsdb',uid,password,model,method,args,kw)
def upsert(model,domain,values):
 ids=call(model,'search',[domain])
 if ids:call(model,'write',[ids,values]);return ids[0]
 return call(model,'create',[values])
program=call('g2p.program.definition','search',[[['program_mnemonic','=','NG_LAB_FARMER']]])[0]
benefit=call('g2p.benefit.codes','search',[[['benefit_mnemonic','=','NG_LAB_CASH']]])[0]
cycle=call('g2p.enrollment.cycle','search',[[['program_id','=',program]]])[0]
call('g2p.enrollment.cycle','write',[[cycle],{'approved_for_enrollment':True,'enrollment_cycle_id':'NG-LAB-ENROLLMENT-001'}])
upsert('g2p.eligibility.rule.definition',[['mnemonic','=','NG_LAB_SYNTHETIC_ONLY']],{'mnemonic':'NG_LAB_SYNTHETIC_ONLY','program_id':program,'target_registry':'farmer','pbms_domain':"[('link_registry_id', 'like', 'NG-LAB-')]"})
upsert('g2p.entitlement.rule.definition',[['mnemonic','=','NG_LAB_ENTITLEMENT']],{'mnemonic':'NG_LAB_ENTITLEMENT','program_id':program,'benefit_code_id':benefit,'quantity':25000,'target_registry':'farmer','pbms_domain':"[('link_registry_id', 'like', 'NG-LAB-')]"})
listing=upsert('g2p.beneficiary.list',[['mnemonic','=','NG_LAB_ELIGIBILITY_TEST']],{'mnemonic':'NG_LAB_ELIGIBILITY_TEST','enrollment_cycle_id':cycle,'brief':'Synthetic fixture-only enrollment verification; no government policy.','eligibility_process_status':'pending'})
print('Synthetic-only eligibility job prepared:',listing)
print(call('g2p.beneficiary.list','read',[[listing]],{'fields':['mnemonic','eligibility_process_status','number_of_registrants','eligibility_latest_error_code']}))
