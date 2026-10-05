import subprocess,pathlib,yaml,xmlrpc.client
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
ip=subprocess.check_output(['kubectl','get','svc','portal-backend-odoo','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
url='http://'+ip
uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate('portalpbmsdb','admin@nigeria.openg2p.localhost',password,{})
if not uid:raise RuntimeError('Portal backend authentication failed')
m=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
def call(model,method,args,kw={}):return m.execute_kw('portalpbmsdb',uid,password,model,method,args,kw)
call('ir.module.module','update_list',[])
names=['g2p_programs','g2p_portal_auth','g2p_auth_id_oidc','g2p_formio','g2p_program_registrant_info','g2p_theme','g2p_program_documents']
ids=call('ir.module.module','search',[[['name','in',names],['state','=','uninstalled']]])
print('Installing',len(ids),'matching beneficiary programme modules',flush=True)
if ids:call('ir.module.module','button_immediate_install',[ids])
country=call('res.country','search',[[['code','=','NG']]])[0]
currency=call('res.currency','search',[[['name','=','NGN']]],{'context':{'active_test':False}})[0]
call('res.currency','write',[[currency],{'active':True}]);call('res.company','write',[[1],{'name':'Nigeria Beneficiary UX Demo','country_id':country,'currency_id':currency}])
call('ir.config_parameter','set_param',['web.base.url','https://portal-admin.openg2p.localhost'])
for model in ['auth.oauth.provider','g2p.program','res.partner','g2p.id.type']:
 fields=call(model,'fields_get',[],{'attributes':['type','required','selection','relation']})
 pathlib.Path('/opt/openg2p-lab/portal-'+model+'.json').write_text(__import__('json').dumps(fields,indent=2))
print('Beneficiary backend modules initialized.')
