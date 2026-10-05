import subprocess,pathlib,yaml,xmlrpc.client,json
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
fixture=json.loads(pathlib.Path('/opt/openg2p-lab/nigeria-fixtures.json').read_text())
for service,db in [('registry-odoo','socialregistrydb'),('pbms-odoo','pbmsdb')]:
    ip=subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    uid=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate(db,'admin@nigeria.openg2p.localhost',password,{})
    m=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object')
    def call(model,method,args,kw={}):return m.execute_kw(db,uid,password,model,method,args,kw)
    def upsert(model,domain,values):
        ids=call(model,'search',[domain])
        if ids:call(model,'write',[ids,values]);return ids[0]
        return call(model,'create',[values])
    if service=='pbms-odoo':
        groups=call('ir.model.data','search_read',[[['model','=','res.groups'],['module','in',['g2p_pbms','g2p_pbms_program_access']]]],{'fields':['res_id']})
        call('res.users','write',[[uid],{'groups_id':[(4,g['res_id']) for g in groups]}])
    country=call('res.country','search',[[['code','=','NG']]])[0]
    currency=call('res.currency','search',[[['name','=','NGN']]],{'context':{'active_test':False}})[0]
    call('res.currency','write',[[currency],{'active':True}])
    call('res.company','write',[[1],{'name':'Nigeria OpenG2P UX Lab','country_id':country,'currency_id':currency}])
    call('ir.config_parameter','set_param',['web.base.url', 'https://'+('registry' if service=='registry-odoo' else 'pbms')+'.openg2p.localhost'])
    if service=='registry-odoo':
        household_ids={}
        for i in range(6):
            reference=f'NG-LAB-HH-{i+1:03d}'
            household_ids[reference]=upsert('res.partner',[['ref','=',reference]],{'name':f'Lab Household {i+1:02d}','ref':reference,'is_registrant':True,'is_group':True,'country_id':country,'comment':'Synthetic Nigeria UX lab household.'})
        for person in fixture['people']:
            rid=upsert('res.partner',[['ref','=',person['individual_id']]],{'name':person['full_name'],'given_name':person['given_name'],'family_name':person['fathers_name'],'ref':person['individual_id'],'is_registrant':True,'is_group':False,'country_id':country,'birthdate':f"{person['birth_year']}-01-01",'email':person['individual_id'].lower()+'@example.invalid','comment':'Synthetic Nigeria UX lab person; no real identity or bank data.'})
            fields=call('g2p.group.membership','fields_get',[],{'attributes':['type','required','relation']})
            vals={}
            for key,value in fields.items():
                if value.get('relation')=='res.partner':
                    if 'group' in key:vals[key]=household_ids[person['household_id']]
                    elif 'individual' in key or 'member' in key:vals[key]=rid
            if vals and not call('g2p.group.membership','search',[[[k,'=',v] for k,v in vals.items()]]):call('g2p.group.membership','create',[vals])
        print('Social Registry: 12 synthetic individuals and 6 households seeded.')
    else:
        agency=upsert('g2p.agency',[['agency_mnemonic','=','NIGERIA_UX_LAB']],{'name':'Nigeria UX Lab — Test Programme Office','agency_mnemonic':'NIGERIA_UX_LAB','admin_email':'admin@nigeria.openg2p.localhost'})
        benefit=upsert('g2p.benefit.codes',[['benefit_mnemonic','=','NG_LAB_CASH']],{'benefit_mnemonic':'NG_LAB_CASH','benefit_type':'CASH_DIGITAL','benefit_description':'Synthetic cash benefit for UX testing; no government policy or live payment.','measurement_unit':'NGN'})
        for mnemonic,description,target in [('NG_LAB_HOUSEHOLD','Nigeria Household Support — UX Demo','other'),('NG_LAB_FARMER','Nigeria Farmer Support — UX Demo','farmer')]:
            program=upsert('g2p.program.definition',[['program_mnemonic','=',mnemonic]],{'program_mnemonic':mnemonic,'description':description,'target_registry':target,'program_status':'ACTIVE','enrollment_frequency':'OnDemand','disbursement_frequency':'OnDemand','beneficiary_list':'latest_always'})
            upsert('g2p.program.benefit.codes',[['program_id','=',program],['benefit_code_id','=',benefit]],{'program_id':program,'benefit_code_id':benefit,'max_quantity':25000})
            upsert('g2p.enrollment.cycle',[['cycle_mnemonic','=',mnemonic+'_2026_10']],{'cycle_number':1,'cycle_mnemonic':mnemonic+'_2026_10','program_id':program,'enrollment_start_date':'2026-10-01','enrollment_end_date':'2026-10-31','disbursement_start_date':'2026-10-01','disbursement_end_date':'2026-10-31'})
        for person in fixture['people'][:6]:
            upsert('g2p.farmer.registry',[['link_registry_id','=',person['individual_id']]],{'link_registry_id':person['individual_id'],'name':person['full_name'],'gender':person['gender'].lower(),'land_area':1.5,'annual_income':180000,'large_area_code':'Kano','small_area_code':'Dala'})
        print('PBMS: Nigerian currency, two demo programmes, benefit, cycles and six farmer fixtures seeded.')
