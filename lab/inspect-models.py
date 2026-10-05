import subprocess,pathlib,yaml,xmlrpc.client,json
p=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
for service,db in [('registry-odoo','socialregistrydb'),('pbms-odoo','pbmsdb')]:
    ip=subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    uid=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate(db,'admin@nigeria.openg2p.localhost',p,{})
    m=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object')
    def call(model,method,args,kw={}):return m.execute_kw(db,uid,p,model,method,args,kw)
    models=call('ir.model','search_read',[[['model','ilike','g2p']]],{'fields':['model','name']})
    print(service,json.dumps(models))
    for model in ['res.partner']+([x['model'] for x in models if any(t in x['model'] for t in ['program','registry.type','eligibility','entitlement','cycle'])] if service=='pbms-odoo' else []):
        fields=call(model,'fields_get',[],{'attributes':['type','required','relation','selection']})
        print(model,json.dumps({k:v for k,v in fields.items() if v.get('required') or (k not in ['message_ids','message_follower_ids'] and not k.startswith('message_') and any(t in k for t in ['name','program','amount','benef','regist','house','gender','birth','date','state','country','is_group','is_registrant','manager','currency','code']))}))
