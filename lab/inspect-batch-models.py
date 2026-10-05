import sys,pathlib,json,subprocess,xmlrpc.client,yaml
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
root=pathlib.Path('/opt/openg2p-lab'); out={}
password=yaml.safe_load((root/'credentials.yaml').read_text())['admin_password']
for svc,db,models in [('registry-odoo','socialregistrydb',['res.partner','g2p.group.membership']),('pbms-odoo','pbmsdb',['g2p.program.definition','g2p.program.benefit.codes','g2p.enrollment.cycle','g2p.farmer.registry']),('portal-backend-odoo','portalpbmsdb',['res.partner','g2p.program','g2p.program.membership','g2p.reg.id','formio.builder'])]:
 ip=subprocess.check_output(['kubectl','get','svc',svc,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip();url='http://'+ip
 uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(db,'admin@nigeria.openg2p.localhost',password,{})
 proxy=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object');out[db]={}
 for model in models:
  try:out[db][model]=proxy.execute_kw(db,uid,password,model,'fields_get',[],{'attributes':['type','required','selection','relation','readonly']})
  except xmlrpc.client.Fault:out[db][model]={'missing':True}
for db in ['register','partner_management','awe']:
 out[db]=json.loads(query(db,"SELECT coalesce(json_agg(row_to_json(t)),'[]'::json) FROM (SELECT table_name,column_name,data_type,column_default,is_nullable FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position)t;"))
(root/'batch-models.json').write_text(json.dumps(out,indent=2))
for db,models in out.items():
 if isinstance(models,dict):
  for model,fields in models.items():print(db,model,'Required:',{k:v for k,v in fields.items() if isinstance(v,dict) and v.get('required') and not v.get('readonly')},'States:',{k:v.get('selection') for k,v in fields.items() if isinstance(v,dict) and v.get('selection')})
 else:print(db,'Tables:',sorted(set(x['table_name'] for x in models)))
