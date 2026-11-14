"""Native household survey parity with 27_meeting_edited, 02:30–05:45."""
from pathlib import Path
HH='a0000000-0000-4000-8000-000000000002';IND='a0000000-0000-4000-8000-000000000001'
ASSETS={'radio':'Radio','television':'Television','generator':'Generator','mobile_phone':'Mobile phone','torch_light':'Torch light','kerosene_stove':'Kerosene stove','fixed_telephone':'Fixed telephone','house':'House (current residence)','land':'Land','refrigerator':'Refrigerator','freezer':'Freezer','sofa':'Furniture (sofa set)','table':'Furniture (table)','hifi':'Hi-fi','mattress':'Mattress','bed':'Bed','computer':'Computer','washing_machine':'Washing machine'}
HOUSE_NEW={'survey_serial_number':'str','household_heads_count':'int','head_list_complete':'str','major_shock_experienced':'str','shock_types':'list','owns_assets':'str','grows_crops':'str','crops_grown':'list','registration_confirmed':'str'}
for a in ASSETS:HOUSE_NEW['owns_'+a]='str'
for a in ['television','generator']:HOUSE_NEW[a+'_count']='int'
MEMBER_NEW={k:'str' for k in ['contact_phone','nin_status','nin_id_type','nimc_surname','nimc_first_name','nimc_other_names','bank_account_number','bvn','work_activity','highest_education','school_enrolled','healthcare_facility_use','severe_disability','social_group_member']}
for k in ['birth_year','birth_month','birth_day']:MEMBER_NEW[k]='int'
INCOME=['Rain-fed crop farming','Irrigated crop farming','Livestock','Fishing','Informal trade / services','Salaried employment','Casual labour','Pension','Remittances','Social assistance','Other']
SHOCKS=['Flood','Drought','Conflict / violence','Epidemic','Storm','Fire','Other']
CROPS=['Beans (Cowpea)','Cassava','Kolanut','Maize','Millet','Oil palm','Rice','Sorghum','Yam','Groundnut','Cocoa','Vegetables','Other']
WORK=['Crop farming','Livestock','Fishing','Salaried employment','Trade / services','Casual labour','Household care','Student','Unemployed','Retired','Other']
EDUCATION=['None','Primary','Junior secondary','Senior secondary','Vocational / technical','Diploma / NCE','University degree','Postgraduate','Other']

def options(values):return [{'label':v,'value':v} for v in values]
def widget(field,label,kind='text',choices=None,required=False,reg=HH,when=None):
 w={'widget':kind,'widget-id':field,'widget-type':'input','widget-label':label,'widget-required':required,'widget-readonly':False,'widget-data-path':reg+'.'+field}
 if choices is not None:w['widget-data-source']={'type':'static','options':choices}
 if when:w['widget-options']={'action':'show','condition':{'field':reg+'.'+when[0],'operator':'equals','value':when[1]}}
 return w
YESNO=[{'label':'Yes','value':'YES'},{'label':'No','value':'NO'}]
def yn(f,label,**kw):return widget(f,label,'radio',YESNO,**kw)
def count(f,label,**kw):return widget(f,label,'select',[{'label':str(i),'value':i} for i in range(1,21)],**kw)
def schema(sid,title,widgets):return {'section-id':sid,'section-title':title,'section-editable':True,'panels':[{'panel-id':'survey_'+sid,'panel-orientation':'vertical','widgets':widgets}]}
