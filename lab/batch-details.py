import pathlib,json,sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
d=json.loads(pathlib.Path('/opt/openg2p-lab/batch-models.json').read_text())
for db,models in [('pbmsdb',['g2p.program.definition','g2p.enrollment.cycle','g2p.farmer.registry']),('portalpbmsdb',['g2p.program.membership','g2p.program'])]:
 for model in models:
  print(db,model,{k:v for k,v in d[db][model].items() if isinstance(v,dict) and k not in ['tz'] and (v.get('required') or v.get('selection') or model=='g2p.program.membership')})
for db,tables in [('register',['g2p_register_individuals','g2p_register_households']),('partner_management',['pm_partners','pm_partner_requests']),('awe',['approval_request'])]:
 for table in tables:print(db,table,[x for x in d[db] if x['table_name']==table])
print('Geo',query('master_data',"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%geo%';"))
print('Portal models',query('portalpbmsdb',"SELECT model FROM ir_model WHERE model LIKE '%membership%' OR model LIKE '%application%';",'portal-backend-postgresql','portal-backend-postgresql'))

