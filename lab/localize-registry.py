import subprocess,pathlib,json,sys,importlib.util
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
code=subprocess.check_output(['kubectl','exec','-n','nigeria','seed-inspect','--','cat','/seed/sync_geo_widgets.py'],text=True)
# Reuse the upstream traversal function; database writes are scoped to our lab metadata.
ns={};exec(code.split('def main():')[0].replace('import psycopg2\n','').replace('import psycopg2.extras\n',''),ns)
levels=[('country','Country'),('state','State / FCT'),('lga','Local Government Area')]
q=lambda s:"'"+s.replace("'","''")+"'"
for table,id_fields in [('g2p_register_sections',['register_id','section_id']),('g2p_intake_form_definitions',['intake_form_id'])]:
 columns=query('register',f"SELECT column_name FROM information_schema.columns WHERE table_name={q(table)} AND data_type='jsonb';").splitlines()
 for column in columns:
  if 'schema' not in column:continue
  rows=query('register',f'SELECT row_to_json(t) FROM {table} t;').splitlines()
  for line in rows:
   row=json.loads(line);schema=row.get(column)
   if not isinstance(schema,dict):continue
   ns['sync_section'](schema,levels)
   widgets=list(ns['walk_widgets'](schema))
   labels={'region':'State / FCT','zone':'Local Government Area','sub_city':'Local Government Area','woreda':'District / locality (optional)','kebele':'Community (optional)'}
   for widget in widgets:
    source=widget.get('widget-data-source')
    if isinstance(source,dict) and source.get('endpoint')=='geo-level-values' and source.get('level_id'):
     source.setdefault('params',{})['level_id']=source['level_id']
     source['valueKey']='level_value_id';source['labelKey']='level_value_mnemonic'
    label=str(widget.get('widget-label','')).lower()
    for old,new in labels.items():
     if label==old or (old=='zone' and label in ['zone / subcity','zone_or_subcity']):widget['widget-label']=new
   where=' AND '.join(k+'='+q(str(row[k])) for k in id_fields)
   query('register',f'UPDATE {table} SET {column}={q(json.dumps(schema))}::jsonb WHERE {where};')
for table in ['g2p_register_individuals','g2p_register_households']:
 query('register',f"UPDATE {table} SET geo_code_hierarchy_json=jsonb_build_object('region',left(geo_lowest_level_value_id,4),'sub_city',geo_lowest_level_value_id),address_line_1='Synthetic UX lab address' WHERE created_by='nigeria-lab';")
query('register',"UPDATE registry_languages SET domain_translation=replace(replace(replace(replace(domain_translation::text,'Zone / Subcity','Local Government Area'),'Woreda','District / locality'),'Kebele','Community'),'Fayda ID','Lab Identity ID')::json;")
print('Registry geography forms localized to Nigeria State/FCT and LGA.')
