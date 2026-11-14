import json,re
from pathlib import Path
from test_mbr_db_connection import connect
ROOT=Path(__file__).parent;locale=ROOT/'registry-ui-source/locales/en.json';messages=json.loads(locale.read_text())
labels={'household_info_tab':'Household information','household_membership_tab':'Household membership','household_housing_services_tab':'Housing and basic services','household_programs':'Household programmes','individual_info_tab':'Personal information','individual_household_tab':'Household membership','individual_livelihood_tab':'Livelihood and employment','individual_vulnerability_tab':'Vulnerability and support needs','individual_programs_tab':'Programme participation','register_mnemonic':'Registry','section_mnemonic':'Section','intake_form_mnemonic':'Registration form','form_mnemonic':'Form name','register_ingest_process_status':'Registry publication status','register_ingest_process_attempts':'Publication attempts','register_ingest_process_last_error_code':'Latest publication error','register_ingest_processed_timestamp':'Publication date and time','draft_status':'Registration status','approval_status':'Approval status','toast_form_save_error':'An error occurred while saving the form','kind':'Task type'}
found=set()
labels.update({'go_back':'Go back','household_location_details':'Household location details','individual_demographic_details':'Personal and demographic details','individual_intake_form':'Individual registration','household_intake_form':'Household registration'})
labels.update({'are_you_sure':'Are you sure?','submit_confirmation_subtitle':'Submit this registration for review. You can make changes if a reviewer returns it for correction.'})
def walk(v):
 if isinstance(v,dict):
  for key,value in v.items():
   if key in ['widget-label','section-title','panel-title','column-label'] and isinstance(value,str) and '_' in value and value not in messages:
    found.add(value)
   walk(value)
 elif isinstance(v,list):
  for value in v:walk(value)
with connect() as c:
 with c.cursor() as q:
  q.execute('SELECT row_to_json(s) FROM g2p_register_sections s')
  for row in q.fetchall():
   walk(row[0].get('section_ui_schema'))
   name=row[0].get('section_mnemonic')
   if isinstance(name,str) and '_' in name and name not in messages:found.add(name)
acronyms={'nin':'NIN','bvn':'BVN','lga':'LGA','id':'ID','gps':'GPS','nimc':'NIMC'}
for key in sorted(found):
 words=key.removesuffix('_tab').split('_');labels.setdefault(key,' '.join(acronyms.get(word,word) for word in words).capitalize())
messages.update(labels);locale.write_text(json.dumps(messages,ensure_ascii=False,indent=2)+'\n')
widget_source=(ROOT/'registry-ui-source/node_modules/@openg2p/registry-widgets/dist/index.esm.js').read_text()
table_copy={'addRecord':'Add record','clickToAdd':'Add a record','addRecordDialog':'Add record','editRecordDialog':'Edit record','addError':'Could not add the record','deleteError':'Could not delete the record','saveError':'Could not save changes','confirm':'Confirm','discard':'Discard changes','unsavedChanges':'Unsaved changes','noData':'No records available'}
messages.setdefault('table',{}).update(table_copy)
widget_labels={}
for path in sorted(set(re.findall(r"translate\(['\"]((?:table|common)\.[A-Za-z_]+)",widget_source))):
 group,key=path.split('.')
 bucket=messages.setdefault(group,{})
 if key not in bucket:
  text=re.sub(r'([a-z])([A-Z])',r'\1 \2',key).replace('_',' ')
  bucket[key]=text[0].upper()+text[1:]
 if key=='noData':bucket[key]='No records available'
 widget_labels[path]=bucket[key]
locale.write_text(json.dumps(messages,ensure_ascii=False,indent=2)+'\n')
display={**labels,'Household Membershib':'Household membership','Household Membership':'Household membership','Register Mnemonic':'Registry','Section Mnemonic':'Section','Register Ingest Process Status':'Registry publication status','Draft Status':'Registration status','Approval Status':'Approval status','kind:':'Task type:','NOT_APPLICABLE':'Not applicable','not_applicable':'Not applicable','Not required for this stage':'Not applicable','STAFF_PORTAL':'Online staff registration','ODK_COLLECT':'Mobile registration','NOT_STARTED':'Not started','IN_PROGRESS':'In progress','PROCESSING':'Processing','PROCESSED':'Completed','FAILED':'Failed','DRAFT':'Draft','FINAL':'Submitted','PENDING':'Pending approval','APPROVED':'Approved','REJECTED':'Rejected','CREATE_UNCERTAIN':'Awaiting confirmation','SUBMITTED':'Submitted','Household Programs':'Household programmes','Individual Programs':'Programme participation'}
display.update(widget_labels)
display.update({'Are you sure ?':'Are you sure?','If you submit your application you cannot modified further.':labels['submit_confirmation_subtitle']})
reference_values={}
with connect('master_data') as c:
 with c.cursor() as q:
  q.execute('SELECT value_code,value_display FROM g2p_attribute_values')
  for code,label in q.fetchall():
   if isinstance(code,str) and isinstance(label,str):reference_values.setdefault(code,set()).add(label)
for code,values in reference_values.items():
 if len(values)==1 and code not in display and re.fullmatch(r'[A-Z][A-Z_]+',code):display[code]=next(iter(values))
(ROOT/'registry-ui-source/locales/registry-display-labels.json').write_text(json.dumps(display,ensure_ascii=False,indent=2)+'\n')
out=ROOT.parent/'output/registry-label-verification';out.mkdir(exist_ok=True);(out/'label-inventory.json').write_text(json.dumps({'metadataLabelsAdded':sorted(found),'displayMappings':display,'businessRecordsChanged':False},indent=2));print('Updated',len(labels),'readable labels; audited',len(found),'missing schema labels')
