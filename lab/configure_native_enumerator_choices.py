from pathlib import Path
import json,datetime
from psycopg2.extras import RealDictCursor,Json
from test_mbr_db_connection import connect
backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/('enumerators-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
people=[('Ibrahim Musa','Kano','North West'),('Babatunde Adeleke','Lagos','South West'),('Chukwuma Okonkwo','Enugu','South East'),('Amina Bello','Kaduna','North West'),('Folake Adebayo','Oyo','South West'),('Emeka Nwosu','Anambra','South East'),('Fatima Danjuma','Sokoto','North West'),('Osasogie Igbinovia','Edo','South South'),('Yakubu Garba','Bauchi','North East'),('Nneka Eze','Imo','South East'),('Damilola Ogundipe','Ogun','South West'),('Usman Mohammed','Borno','North East'),('Tari Ebiere','Bayelsa','South South'),('Halima Shehu','Katsina','North West')]
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  q.execute("SELECT * FROM g2p_register_sections WHERE section_id='hh_composition_headship' FOR UPDATE");row=q.fetchone();(backup/'section.json').write_text(json.dumps(row,default=str));schema=row['section_ui_schema'];panels=schema['panels'][0]['panels'];widgets={w['widget-id']:w for p in panels for w in p.get('widgets',[])}
  for field in ['enumerator_name','sponsor_name']:
   if field not in widgets:continue
   q.execute('SELECT DISTINCT '+field+' AS value FROM g2p_intake_form_households WHERE '+field+" IS NOT NULL AND "+field+"<>'' UNION SELECT DISTINCT "+field+' FROM g2p_register_households WHERE '+field+" IS NOT NULL AND "+field+"<>''");existing=[x['value'] for x in q.fetchall()]
   opts=([{'label':f'{n} ({s} State · {z}) — Sample','value':f'SAMPLE: {n} ({s})'} for n,s,z in people] if field=='enumerator_name' else [{'label':x,'value':x} for x in ['NSIPA','NG CARES']])
   for value in existing:
    if value not in [o['value'] for o in opts]:opts.append({'label':value,'value':value})
   if field=='enumerator_name':opts.append({'label':'Other / unlisted enumerator','value':'OTHER_UNLISTED'})
   widgets[field]['widget']='select';widgets[field]['widget-data-source']={'type':'static','options':opts}
  panels[:]=[{'panel-id':'survey_consent','panel-orientation':'vertical','widgets':[widgets[x] for x in ['sponsor_name','consent_status','respondent_name']]},{'panel-id':'survey_enumeration','panel-orientation':'vertical','widgets':[widgets[x] for x in ['survey_community'] if x in widgets]},{'panel-id':'household_basics','panel-orientation':'vertical','widgets':[w for k,w in widgets.items() if k not in ['sponsor_name','consent_status','respondent_name','enumerator_name','survey_community']]}]
  schema['section-title']='Survey Consent & Enumeration / Household details';q.execute('UPDATE g2p_register_sections SET section_ui_schema=%s WHERE section_id=%s',(Json(schema),row['section_id']))
 c.commit()
print(json.dumps({'sample_enumerators':len(people),'existing_values_preserved':True,'backup':str(backup)}))
