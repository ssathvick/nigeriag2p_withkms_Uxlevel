"""Build a versioned Collect survey from the same native section schemas."""
import json,re,xml.etree.ElementTree as E
from pathlib import Path
from psycopg2.extras import RealDictCursor
from test_mbr_db_connection import connect
from household_survey_spec import *
ROOT=Path(__file__).parent
# Reuse the XForms primitives, without running the previous form body.
source=(ROOT/'build_native_collect_form.py').read_text();exec(source[:source.index("visit=group(")]);data.set('version','2026111304')
choices={};paths={};fieldtypes={}
LABELS=json.loads((ROOT/'registry-ui-source/locales/en.json').read_text())
def token(v):return re.sub('[^A-Za-z0-9_.-]','_',str(v)).strip('_') or 'OTHER'
def add(pair,w,fieldname=None,required=None):
 f=fieldname or w['widget-id'];kind=w['widget'];opts=w.get('widget-data-source',{}).get('options');xp='/data/'+pair[0].tag+'/'+f;label=w['widget-label'];label=LABELS.get(label,label.replace('_',' ').capitalize() if '_' in label else label);req=w.get('widget-required',False) if required is None else required
 vals=None
 if opts:
  vals=[(token(o['value']),str(o['label'])) for o in opts];choices[xp]={token(o['value']):o['value'] for o in opts}
 typ='int' if kind=='number' and f not in ['latitude','longitude','monthly_household_income'] else 'decimal' if kind=='number' else 'date' if kind=='date' else 'string'
 when=w.get('widget-data-options',{}).get('condition');relevant=None
 if when:
  cond=when['field'].split('.')[-1];target=paths.get(cond)
  if target:relevant=target+" = '"+token(when['value'])+"'"
 constraint=None
 if f=='estimated_age':constraint='. >= 0 and . <= 120'
 if f=='bank_account_number':constraint="regex(., '^[0-9]{10}$')"
 if f in ['bvn']:constraint="regex(., '^[0-9]{11}$')"
 field(pair,f,label,typ,required=req,options=vals,constraint=constraint,relevant=relevant)
 if kind=='checkbox' and opts:
  ctrl=list(pair[1])[-1];ctrl.tag=x('select')
 paths[f]=xp;fieldtypes[f]=typ
with connect() as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:q.execute("SELECT section_id,section_ui_schema FROM g2p_register_sections WHERE section_id=ANY(%s)",(['hh_survey_consent','hh_composition_headship','hh_members','hh_dwelling_services','hh_income_shocks','hh_health_insurance','hh_possessions','hh_crops'],));schemas={r['section_id']:r['section_ui_schema'] for r in q.fetchall()}
get=lambda sid:schemas[sid]['panels'][0]['widgets']
visit=group('visit','Survey Consent & Enumeration')
for w in get('hh_survey_consent'):
 if w['widget-id'] not in ['address_line_1','latitude','longitude','location_accuracy_m','location_captured_at','location_capture_source','household_geography']:add(visit,w)
house=group('household','Headship & Household Composition')
for w in get('hh_composition_headship'):
 if w['widget-id']!='household_head_internal_record_id':
  if w['widget-id']=='household_heads_count':w['widget-data-source']['options']=[{'label':'1','value':1}]
  add(house,w)
field(house,'address_line_1','Household address (optional)');field(house,'coordinates','GPS coordinates (optional)','geopoint')
# The exact mobile reference catalogue is embedded for offline cascading selection.
geo=group('geography','Nigeria location — State/FCT, LGA and ward')
locations=json.loads((ROOT/'field-app/android/assets/locations.json').read_text())
for key,label,parent in [('state','State / FCT',None),('lga','Local Government Area','state'),('ward','Ward','lga')]:
 name=key+'_id';E.SubElement(geo[0],name);E.SubElement(model,x('bind'),{'nodeset':'/data/geography/'+name,'type':'string'})
 control=E.SubElement(geo[1],x('select1'),{'ref':'/data/geography/'+name});E.SubElement(control,x('label')).text=label
 instance=E.SubElement(model,x('instance'),{'id':'nigeria_'+key});catalog=E.SubElement(instance,'catalog',{'xmlns':''})
 for entry in locations[{'state':'states','lga':'lgas','ward':'wards'}[key]]:
  item=E.SubElement(catalog,'item');E.SubElement(item,'id').text=entry['id'];E.SubElement(item,'name').text=entry['name'];E.SubElement(item,'parent').text=entry.get('parent','')
 path="instance('nigeria_"+key+"')/catalog/item"+("[parent = /data/geography/"+parent+"_id]" if parent else '')
 items=E.SubElement(control,x('itemset'),{'nodeset':path});E.SubElement(items,x('label'),{'ref':'name'});E.SubElement(items,x('value'),{'ref':'id'})
field(house,'location_captured_at','Device location capture time','dateTime',calculate="once(if(string-length(/data/household/coordinates) > 0, now(), ''))")
members=group('members','Household Member Details',repeat=True)
columns=get('hh_members')[0]['widget-data-columns'];seen=set()
for col in columns:
 f=col['column-key']
 if f in ['prefix','suffix'] or f in seen:continue
 seen.add(f);w=dict(col);w['widget-id']=f
 if f=='estimated_age':add(members,w,required="string-length(../birth_date) = 0")
 else:add(members,w)
living=group('living','Household Living & Dwelling Characteristics')
# Retain established field paths, and their published XML data types.
for w in get('hh_dwelling_services'):
 if w['widget-id']=='rooms_count':w=dict(w,widget='number');w.pop('widget-data-source',None)
 if w.get('widget-data-source',{}).get('type')=='api':
  # Use native published attribute values rather than inventing survey codes.
  attr=w['widget-data-source']['params']['attribute_id']
  with connect('master_data') as c:
   with c.cursor(cursor_factory=RealDictCursor) as q:q.execute('SELECT value_code,value_display FROM g2p_attribute_values WHERE attribute_id=%s ORDER BY sort_order',(attr,));entries=q.fetchall()
  w['widget-data-source']={'type':'static','options':[{'label':e['value_display'],'value':e['value_code']} for e in entries]}
 add(living,w)
income=group('income','Household Income, Vulnerability to Shocks & Coping')
for w in get('hh_income_shocks'):add((living[0],income[1]) if w['widget-id'] in ['income_source','monthly_household_income'] else income,w)
insurance=group('insurance','Health Insurance Coverage')
for w in get('hh_health_insurance'):add((living[0],insurance[1]),w)
possessions=group('possessions','Household Assets & Possessions')
for w in get('hh_possessions'):add(possessions,w)
crops=group('crops','Crops Grown')
for w in get('hh_crops'):add(crops,w)
# Keep the original additional-asset repeat for already downloaded client forms.
assets=group('assets','Additional asset details (optional)',repeat=True)
field(assets,'asset_type','Asset type',options=[(v,v.title().replace('_',' ')) for v in ['LAND','LIVESTOCK','PRODUCTIVE_TOOL','CONSUMER_DURABLE','VEHICLE','OTHER']]);field(assets,'asset_category','Asset description');field(assets,'quantity','Quantity','int',constraint='. >= 0')
review=group('review','Review and confirmation');field(review,'confirmation','I confirm these household records are accurate and understand that registration does not guarantee programme eligibility.',required=True,options=[('YES','Reviewed and confirmed')],constraint="count(/data/members[relationship_to_head = 'SELF']) = 1 and count(/data/members) >= 1")
meta=E.SubElement(data,'meta');E.SubElement(meta,'instanceID');E.SubElement(model,x('bind'),{'nodeset':'/data/meta/instanceID','type':'string','readonly':'true()','calculate':"once(concat('uuid:', uuid()))"})
E.ElementTree(root).write(ROOT/'household-parity/nsipa_registry_household.xml',encoding='utf-8',xml_declaration=True);(ROOT/'household-parity/odk_survey_choices.json').write_text(json.dumps({'choices':choices,'paths':paths,'fieldtypes':fieldtypes},indent=2));print('Generated expanded Collect form with',len(paths),'fields')
