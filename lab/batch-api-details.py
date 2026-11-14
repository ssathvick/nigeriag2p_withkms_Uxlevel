exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-batch-models.py').read().split('for svc,db,models')[0])
import requests
for svc,key in [('commons-services-pm-staff-portal-api','pm'),]:
 ip=subprocess.check_output(['kubectl','get','svc',svc,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
 r=requests.get('http://'+ip+'/openapi.json');r.raise_for_status();data=r.json();(root/('batch-'+key+'-api.json')).write_text(json.dumps(data))
 print(key,[(p,list(methods)) for p,methods in data['paths'].items() if any(x in p for x in ['onboard','approve','reject','disable','requests'])])
url='http://'+subprocess.check_output(['kubectl','get','svc','portal-backend-odoo','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate('portalpbmsdb','admin@nigeria.openg2p.localhost',password,{})
m=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
for model in ['g2p.program_membership','g2p.program','formio.form']:
 fields=m.execute_kw('portalpbmsdb',uid,password,model,'fields_get',[],{'attributes':['type','selection','required','relation']})
 (root/('batch-'+model+'.json')).write_text(json.dumps(fields))
 print(model,{k:v for k,v in fields.items() if k in ['partner_id','program_id','state','registrant_id','name','builder_id','submission_data','submission_date','title'] or v.get('required') and k not in ['tz']})
print('Geo',query('master_data',"SELECT column_name FROM information_schema.columns WHERE table_name='g2p_geo_level_values';"))
