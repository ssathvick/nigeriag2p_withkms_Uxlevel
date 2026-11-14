import ast,copy,datetime,json,subprocess,uuid
from pathlib import Path
from psycopg2 import sql
from psycopg2.extras import Json,RealDictCursor
from test_mbr_db_connection import connect
from household_survey_spec import *
ROOT=Path(__file__).parent;PATCH=ROOT/'meeting-native/patched/register-staff-portal-api';backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/('household-parity-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True)
def run(*args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
changes_path=ROOT/'meeting-native/changes.json';changes=json.loads(changes_path.read_text());files={}
for subject,fields,cls in [('household',HOUSE_NEW,'Household'),('individual',MEMBER_NEW,'Individual')]:
 for group in ['models','schemas']:
  rel='reference/'+group+'/'+subject+'.py';p=PATCH/rel;target='/usr/local/lib/python3.12/site-packages/openg2p_registry_reference_extension/register_domain/'+group+'/'+subject+'.py'
  if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(run('kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','cat',target))
  source=p.read_text();(backup/(group+'-'+subject+'.py')).write_text(source)
  if '# household-survey-parity' not in source:
   block='\n    # household-survey-parity: additive, nullable, shared by intake/master/history.\n'
   if group=='models':
    source='from sqlalchemy import JSON as SurveyJSON\n'+source
    for field,kind in fields.items():block+=f'    {field}: Mapped[{"list" if kind=="list" else kind}] = mapped_column({dict(str="String",int="Integer",list="SurveyJSON")[kind]}, nullable=True)\n'
    anchor='class G2P'+cls+':'
   else:
    for field,kind in fields.items():block+=f'    {field}: Optional[{kind}] = None\n'
    anchor='class G2PSchema'+cls+':'
   source=source.replace(anchor,anchor+'\n'+block,1);ast.parse(source);p.write_text(source)
  files[str(p.relative_to(ROOT/'meeting-native')).replace('\\','/')]=target;changes['register-staff-portal-api'].update(files)
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:
  for subject,fields in [('households',HOUSE_NEW),('individuals',MEMBER_NEW)]:
   for prefix in ['g2p_intake_form_','g2p_register_','g2p_register_history_']:
    for field,kind in fields.items():q.execute(sql.SQL('ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} '+{'str':'varchar','int':'integer','list':'json'}[kind]).format(sql.Identifier(prefix+subject),sql.Identifier(field)))
  q.execute('SELECT * FROM g2p_register_sections');rows=q.fetchall();byid={r['section_id']:r for r in rows};(backup/'sections.json').write_text(json.dumps(rows,default=str))
  q.execute("SELECT * FROM g2p_intake_form_ui_tab_sections WHERE tab_id='form_tab_household_intake'");(backup/'intake-links.json').write_text(json.dumps(q.fetchall(),default=str))
  def widgets_of(node):
   found=[]
   if isinstance(node,dict):
    if 'widget-id' in node:found.append(node)
    for v in node.values():found+=widgets_of(v)
   elif isinstance(node,list):
    for v in node:found+=widgets_of(v)
   return found
  old={w['widget-id']:w for w in widgets_of(byid['hh_composition_headship']['section_ui_schema'])}
  survey=[old[x] for x in ['sponsor_name','consent_status','respondent_name','enumerator_name','survey_community']]
  sponsor=survey[0];sponsor['widget-data-source']['options']+= [o for o in options(['UNICEF','GIZ','STATE SPONSORED','WORLD FOOD PROGRAMME','Others']) if o['value'] not in [x['value'] for x in sponsor['widget-data-source']['options']]]
  survey[1]['widget-label']='Consent to share data (including NIN) for social protection programmes';survey[1]['widget']='radio'
  survey += [widget('survey_serial_number','Survey serial number'),widget('address_line_1','Household address'),widget('latitude','Latitude','number'),widget('longitude','Longitude','number')]
  composition=[old[x] for x in ['record_name','household_head_name','household_head_internal_record_id','headship_type']]+[count('household_heads_count','Total number of household heads'),yn('head_list_complete','Is this the complete list of household heads?')]
  dwelling=[w for w in widgets_of(byid['hh_dwelling_services']['section_ui_schema']) if w['widget-id'] not in ['monthly_household_income','income_source','health_insurance_status']]
  for w in dwelling:
   if w['widget-id']=='rooms_count':w.update(count('rooms_count','Number of rooms occupied by household'))
  income=[widget('income_source','Main source of household income','select',options(INCOME)),widget('monthly_household_income','Monthly household income (optional)','number'),yn('major_shock_experienced','Affected by any major shock in the past 3 years?'),widget('shock_types','Major shocks experienced','checkbox',options(SHOCKS),when=('major_shock_experienced','YES'))]
  assets=[yn('owns_assets','Does the household own any of the following assets?')]
  for key,label in ASSETS.items():
   assets.append(yn('owns_'+key,label,when=('owns_assets','YES')))
   if key in ['television','generator']:assets.append(count(key+'_count','Number of '+('televisions' if key=='television' else 'generators')+' owned',when=('owns_'+key,'YES')))
  section_specs=[('hh_survey_consent','Survey Consent & Enumeration',survey),('hh_composition_headship','Headship & Household Composition',composition),('hh_members','Household Member Details',None),('hh_dwelling_services','Household Living & Dwelling Characteristics',dwelling),('hh_income_shocks','Household Income, Vulnerability to Shocks & Coping',income),('hh_health_insurance','Health Insurance Coverage',[yn('health_insurance_status','Is anyone in the household covered by health insurance?')]),('hh_possessions','Household Assets & Possessions',assets),('hh_crops','Crops Grown',[yn('grows_crops','Does the household grow any crops?'),widget('crops_grown','Crops grown','checkbox',options(CROPS),when=('grows_crops','YES'))])]
  for i,(sid,title,widgets) in enumerate(section_specs):
   row=copy.deepcopy(byid.get(sid,byid['hh_composition_headship']));row.update(section_id=sid,section_mnemonic=title,section_description=title)
   if widgets is not None:row['section_ui_schema']=schema(sid,title,widgets)
   else:
    table=row['section_ui_schema']['panels'][0]['widgets'][0];table['widget']='dialog-table';table['widget-data-add-label']='Add Household Member';table['widget-data-visible-columns']=['last_name','first_name','relationship_to_head','gender','estimated_age','nin_status'];columns=table['widget-data-columns'];cols={w['column-key']:w for w in columns}
    def member(f,label,kind='text',choices=None,when=None):
     w=widget(f,label,kind,choices,reg=IND,when=when);w.pop('widget-id');w['column-key']=f;w['widget-data-path']=f
     if when:w['widget-options']['condition']['field']=when[0]
     return w
    additions=[member('marital_status','Marital status','select',options(['SINGLE','MARRIED','DIVORCED','WIDOWED','SEPARATED','UNKNOWN'])),member('contact_phone','Contact phone number'),member('nin_status','Has a NIN or tracking number?','radio',YESNO),member('nin_id_type','Identification type','radio',options(['NIN','TRACKING_NUMBER']),('nin_status','YES')),member('nimc_surname','Surname (as on NIMC slip)'),member('nimc_first_name','First name (as on NIMC slip)'),member('nimc_other_names','Other names (as on NIMC slip)'),member('bank_account_number','Bank account number (10 digits)'),member('bvn','Bank Verification Number (11 digits)'),member('work_activity','Primary work activity (past 12 months)','select',options(WORK)),member('highest_education','Highest educational qualification','select',options(EDUCATION)),member('school_enrolled','Currently enrolled in school?','radio',YESNO),member('healthcare_facility_use','Uses a healthcare facility?','radio',YESNO),member('severe_disability','Has any severe disability?','radio',YESNO),member('chronic_illness_flag','Has a chronic illness?','boolean'),member('social_group_member','Belongs to a social network or group?','radio',YESNO),member('birth_year','Birth year (if full date unknown)','number'),member('birth_month','Birth month (if known)','number'),member('birth_day','Birth day (if known)','number')]
    for w in additions:
     if w['column-key'] not in cols:columns.append(w)
    cols['foundational_id']['widget-label']='NIN (11 digits; not authenticated)';cols['rid']['widget-label']='NIN tracking number';cols['prefix']['column-visible-in-table']=False;cols['suffix']['column-visible-in-table']=False
    row['section_ui_schema']['section-title']=title
   cols=list(row);q.execute(sql.SQL('INSERT INTO g2p_register_sections ({}) VALUES ({}) ON CONFLICT (section_id) DO UPDATE SET section_mnemonic=EXCLUDED.section_mnemonic,section_description=EXCLUDED.section_description,section_ui_schema=EXCLUDED.section_ui_schema').format(sql.SQL(',').join(map(sql.Identifier,cols)),sql.SQL(',').join(sql.Placeholder()*len(cols))),[Json(row[k]) if k=='section_ui_schema' else row[k] for k in cols])
   q.execute("UPDATE g2p_intake_form_ui_tab_sections SET section_order=section_order+100 WHERE tab_id='form_tab_household_intake' AND section_id=%s AND section_order<100",(sid,))
   q.execute("SELECT tab_section_id FROM g2p_intake_form_ui_tab_sections WHERE tab_id='form_tab_household_intake' AND section_id=%s",(sid,));link=q.fetchone()
   if link:q.execute('UPDATE g2p_intake_form_ui_tab_sections SET section_order=%s WHERE tab_section_id=%s',(i+1,link['tab_section_id']))
   else:q.execute('INSERT INTO g2p_intake_form_ui_tab_sections VALUES (%s,%s,%s,%s)',(str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-survey-intake-'+sid)),'form_tab_household_intake',sid,i+1))
   q.execute("SELECT tab_section_id FROM g2p_register_ui_tab_sections WHERE register_id=%s AND section_id=%s",(HH,sid))
   if not q.fetchone():q.execute('INSERT INTO g2p_register_ui_tab_sections VALUES (%s,%s,%s,%s,%s)',(str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-survey-master-'+sid)),HH,'household_info_tab',sid,(i+1)*10+5))
  q.execute("UPDATE g2p_intake_form_ui_tab_sections SET section_order=section_order+100 WHERE tab_id='form_tab_household_intake' AND section_id<>ALL(%s) AND section_order<100",([x[0] for x in section_specs],))
 c.commit()
changes_path.write_text(json.dumps(changes,indent=2));(ROOT/'household-parity/section-specs.json').write_text(json.dumps(section_specs,default=str,indent=2))
# Update existing ConfigMaps and add the two individual modules, preserving all other native fixes.
for deployment in ['register-staff-portal-api','register-celery-worker','register-celery-beat-producer','register-partner-api','registry-bg-tasks-worker','registry-bg-tasks-producer','register-id-generator']:
 d=json.loads(run('kubectl','-n','nigeria','get','deploy',deployment,'-o','json'));(backup/(deployment+'.json')).write_text(json.dumps(d));spec=d['spec']['template']['spec'];container=spec['containers'][0];name='native-household-parity';data={};mounts=[]
 for i,(source,target) in enumerate(files.items()):
  key='f'+str(i);data[key]=(ROOT/'meeting-native'/source).read_text();mounts.append({'name':name,'mountPath':target,'subPath':key,'readOnly':True})
 cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':name,'namespace':'nigeria'},'data':data};run('kubectl','apply','--server-side','--field-manager=household-parity','-f','-',input=json.dumps(cm))
 spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!=name]+[{'name':name,'configMap':{'name':name}}];targets=set(files.values());container['volumeMounts']=[m for m in container.get('volumeMounts',[]) if m['mountPath'] not in targets]+mounts;specmeta=d['spec']['template'].setdefault('metadata',{});specmeta.setdefault('annotations',{})['household-survey-release']=datetime.datetime.now().isoformat();run('kubectl','replace','-f','-',input=json.dumps(d))
print(json.dumps({'status':'deployed','backup':str(backup),'householdFields':len(HOUSE_NEW),'memberFields':len(MEMBER_NEW),'nativeSections':8,'recordsModified':0}))
