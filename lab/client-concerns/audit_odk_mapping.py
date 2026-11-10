import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from labdb import query
out={}
with r.pg('register') as c:
 with c.cursor() as q:
  for t in ['g2p_registry_import_file_configurations','incoming_templates','incoming_model_key_paths','data_models']:
   q.execute('SELECT row_to_json(t) FROM '+t+' t');out[t]=[x[0] for x in q.fetchall()]
print('Native import configuration counts:',{k:len(v) for k,v in out.items()})
for sql in ["SELECT count(*) FROM odk_config", "SELECT id,name,base_url,project,form_id FROM odk_config", "SELECT id,odk_config,json_formatter,target_registry,job_status FROM odk_import"]:
 try:print(query('socialregistrydb',sql,host_service='registry-postgresql',secret_name='registry-postgresql'))
 except Exception as e:print(type(e).__name__,str(e)[:200])
Path(__file__).with_name('odk-native-config-audit.json').write_text(json.dumps(out,indent=2,default=str))
