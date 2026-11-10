import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
out={}
for database,tables in {'register':['g2p_registry_configuration','g2p_register_definitions','g2p_register_schemas','g2p_registry_awe_policy_configurations','g2p_registry_data_policies','g2p_intake_form_ui_tabs','g2p_intake_form_ui_tab_sections','g2p_input_mechanisms','incoming_templates','incoming_model_key_paths','incoming_model_semantic_patterns','incoming_model_register_semantic_patterns'],'awe':['approval_policy','approval_stage','approver_rule']}.items():
 with r.pg(database) as c:
  with c.cursor() as cur:
   for table in tables:
    cur.execute('SELECT row_to_json(t) FROM '+table+' t');out[table]=[x[0] for x in cur.fetchall()]
with r.pg('register') as c:
 with c.cursor() as cur:
  for table in ['g2p_register_households','g2p_register_household_housing_and_services']:
   cur.execute('SELECT roof_material,water_source_type,count(*) FROM '+table+' GROUP BY 1,2');out[table+'_codes']=cur.fetchall()
  cur.execute('SELECT created_by,count(*) FROM g2p_register_households GROUP BY 1');out['household_sources']=cur.fetchall()
  cur.execute('SELECT submission_source,count(*) FROM g2p_intake_form_submissions GROUP BY 1');out['intake_sources']=cur.fetchall()
with r.pg('odkdb') as c:
 with c.cursor() as cur:
  cur.execute('SELECT id,"xmlFormId" FROM forms WHERE "deletedAt" IS NULL');out['odk_forms']=cur.fetchall()
p=Path(__file__).parent/'details.json';p.write_text(json.dumps(out,indent=2,default=str));p.chmod(0o600)
for key in ['g2p_registry_configuration','g2p_registry_awe_policy_configurations','household_sources','intake_sources','odk_forms','g2p_register_households_codes','g2p_register_household_housing_and_services_codes']:print(key,json.dumps(out[key]))

