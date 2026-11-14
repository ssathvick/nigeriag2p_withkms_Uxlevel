"""Use the installed 1.1.9-dev.2 hierarchy widget instead of colliding selects."""
import sys,json,copy,datetime,os
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
REG='a0000000-0000-4000-8000-000000000002'
def repair(schema):
 result=copy.deepcopy(schema)
 panel=result['panels'][0]['panels'][0]
 assert [w['widget-id'] for w in panel['widgets']]==['region_code','zone_subcity_code','woreda_code']
 panel['widgets']=[{
  'widget':'geo-hierarchy','widget-id':'household_geography','widget-type':'input',
  'widget-label':'Administrative location','widget-readonly':False,'widget-required':False,
  'widget-data-path':{'value':REG+'.geo_lowest_level_value_id','hierarchy':REG+'.geo_code_hierarchy_json'},
  'widget-data-source':{'type':'api','service':'master-data','method':'POST','levelsEndpoint':'get-all-g2p-geo-levels','valuesEndpoint':'geo-level-values'},
  'widget-geo-layout':{'columns':[3],'distribution':'fixed','columnSpan':1}
 }]
 return result
if __name__=='__main__':
 os.umask(0o077)
 with r.pg('register') as c:
  with c.cursor() as q:
   q.execute('SELECT section_ui_schema FROM g2p_register_sections WHERE register_id=%s AND section_id=%s FOR UPDATE',(REG,'hh_location_details'))
   before=q.fetchone()[0]
   after=repair(before)
   backup=Path('/opt/openg2p-lab/backups')/('household-location-schema-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
   backup.write_text(json.dumps(before,indent=2))
   q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s::jsonb WHERE register_id=%s AND section_id=%s',(json.dumps(after),REG,'hh_location_details'))
   assert q.rowcount==1
 print('Updated household location schema; backup:',backup)
