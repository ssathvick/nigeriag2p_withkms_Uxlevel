import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;backup=Path((root/'backup-location.txt').read_text());reg='a0000000-0000-4000-8000-000000000002'
with r.pg('register') as c:
 with c.cursor() as cur:
  cur.execute('SELECT section_ui_schema FROM g2p_register_sections WHERE register_id=%s AND section_id=%s',(reg,'hh_composition_headship'));schema=cur.fetchone()[0];(backup/'household-headship-schema.json').write_text(json.dumps(schema))
  widgets=schema['panels'][0]['panels'][0]['widgets']
  if not any(w.get('widget-id')=='record_name' for w in widgets):widgets[:0]=[{'widget':'text','widget-id':'record_name','widget-type':'input','widget-label':'household_name','widget-required':True,'widget-readonly':False,'widget-data-path':reg+'.record_name'},{'widget':'text','widget-id':'household_head_name','widget-type':'input','widget-label':'household_head_name','widget-required':True,'widget-readonly':False,'widget-data-path':reg+'.household_head_name'}]
  for w in widgets:
   if w.get('widget-id')=='household_head_person_id':w.update({'widget-id':'household_head_internal_record_id','widget-label':'household_head_reference','widget-data-path':reg+'.household_head_internal_record_id'})
  cur.execute('UPDATE g2p_register_sections SET section_ui_schema=%s::jsonb WHERE register_id=%s AND section_id=%s',(json.dumps(schema),reg,'hh_composition_headship'))
  cur.execute('SELECT language_id,domain_translation FROM registry_languages');langs=cur.fetchall();(backup/'registry-language-domain.json').write_text(json.dumps(langs))
  for lid,translations in langs:
   translations.update(household='Households',individual='Individuals',household_name='Household name',household_head_name='Household head',household_head_reference='Household head reference (optional)',functional_record_id='Record reference',roof_material='Roof material',water_source_type='Water source',not_applicable='Not required for this stage',NOT_APPLICABLE='Not required for this stage')
   cur.execute('UPDATE registry_languages SET domain_translation=%s::json WHERE language_id=%s',(json.dumps(translations),lid))
p=root.parent/'persona-ui/src/service-insights.js';s=p.read_text();s=s.replace("if(!shownOnce){shownOnce=true;opened=true;panel.hidden=false;opener.setAttribute('aria-expanded','true')}","if(!shownOnce){shownOnce=true;opened=false;panel.hidden=true;opener.setAttribute('aria-expanded','false')}");p.write_text(s)
print('Required household and head names added; heading translations corrected; overview made opt-in.')
