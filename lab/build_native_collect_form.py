"""Offline representation of native household/head/member/asset fields."""
from pathlib import Path
import xml.etree.ElementTree as E
XF='http://www.w3.org/2002/xforms';H='http://www.w3.org/1999/xhtml';JR='http://openrosa.org/javarosa';ORX='http://openrosa.org/xforms'
E.register_namespace('',XF);E.register_namespace('h',H);E.register_namespace('jr',JR);E.register_namespace('orx',ORX)
def x(name):return '{'+XF+'}'+name
root=E.Element('{'+H+'}html');head=E.SubElement(root,'{'+H+'}head');E.SubElement(head,'{'+H+'}title').text='NSIPA Master Registry Household Interview';model=E.SubElement(head,x('model'));instance=E.SubElement(model,x('instance'));data=E.SubElement(instance,'data',{'xmlns':'','id':'nsipa_registry_household','version':'2026111201'});body=E.SubElement(root,'{'+H+'}body')
def group(name,title,parent=body,repeat=False):
 node=E.SubElement(data,name,{'{'+JR+'}template':''} if repeat else {})
 if repeat:
  outer=E.SubElement(parent,x('group'));E.SubElement(outer,x('label')).text=title;ui=E.SubElement(outer,x('repeat'),{'nodeset':'/data/'+name})
 else:ui=E.SubElement(parent,x('group'),{'ref':'/data/'+name});E.SubElement(ui,x('label')).text=title
 return node,ui
def field(pair,name,label,kind='string',required=False,options=None,constraint=None,relevant=None,calculate=None):
 node,ui=pair;E.SubElement(node,name);path='/data/'+node.tag+'/'+name;attrs={'nodeset':path,'type':kind}
 if required:attrs['required']='true()' if required is True else required
 if constraint:attrs['constraint']=constraint;attrs['{'+JR+'}constraintMsg']='Check this answer before continuing.'
 if relevant:attrs['relevant']=relevant
 if calculate:attrs['calculate']=calculate
 E.SubElement(model,x('bind'),attrs)
 if calculate:return
 control=E.SubElement(ui,x('select1' if options else 'input'),{'ref':path});E.SubElement(control,x('label')).text=label
 for value,text in options or []:
  item=E.SubElement(control,x('item'));E.SubElement(item,x('label')).text=text;E.SubElement(item,x('value')).text=value
visit=group('visit','Sponsor, consent and enumerator')
for name,label in [('sponsor_name','Sponsor'),('respondent_name','Respondent name'),('enumerator_name','Enumerator name')]:field(visit,name,label,required=True)
field(visit,'consent_status','Has informed consent been given?',required=True,options=[('YES','Yes'),('NO','No — stop the interview')],constraint=". = 'YES'")
field(visit,'survey_community','Community or region (optional)')
house=group('household','Household details')
field(house,'record_name','Household name',required=True);field(house,'address_line_1','Address (optional)');field(house,'coordinates','GPS coordinates (optional)','geopoint')
members=group('members','Household members',repeat=True)
for name,label in [('first_name','First name'),('last_name','Last name')]:field(members,name,label,required=True)
field(members,'gender','Sex',required=True,options=[('MALE','Male'),('FEMALE','Female'),('OTHER','Other'),('UNKNOWN','Unknown')])
field(members,'birth_date','Date of birth (leave blank if unknown)','date')
field(members,'estimated_age','Age when date of birth is unknown','int',required="string-length(../birth_date) = 0",constraint='. >= 0 and . <= 120')
field(members,'relationship_to_head','Relationship to household head',required=True,options=[(v,'Household head' if v=='SELF' else v.title().replace('_',' ')) for v in ['SELF','SPOUSE','CHILD','PARENT','SIBLING','OTHER_RELATIVE','NON_RELATIVE']])
field(members,'foundational_id','National ID (optional; authentication is not connected)')
living=group('living','Living conditions and income (optional)')
for name,label in [('rooms_count','Number of rooms'),('monthly_household_income','Monthly household income')]:field(living,name,label,'decimal' if 'income' in name else 'int',constraint='. >= 0')
field(living,'income_source','Main income source')
field(living,'health_insurance_status','Health insurance',options=[('YES','Yes'),('NO','No'),('UNKNOWN','Unknown')])
field(living,'tenure_status','Housing tenure',options=[(v,v.title().replace('_',' ')) for v in ['OWNED','RENTED','SHARED','OTHER']])
assets=group('assets','Household assets (optional)',repeat=True)
field(assets,'asset_type','Asset type',required=True,options=[(v,v.title().replace('_',' ')) for v in ['LAND','LIVESTOCK','PRODUCTIVE_TOOL','CONSUMER_DURABLE','VEHICLE','OTHER']])
field(assets,'asset_category','Asset description');field(assets,'quantity','Quantity','int',constraint='. >= 0')
review=group('review','Review and confirmation')
field(review,'confirmation','I have reviewed these answers and confirm they are ready for submission.',required=True,options=[('YES','Reviewed and confirmed')],constraint="count(/data/members[relationship_to_head = 'SELF']) = 1 and count(/data/members) >= 1")
meta=E.SubElement(data,'meta');E.SubElement(meta,'instanceID');E.SubElement(model,x('bind'),{'nodeset':'/data/meta/instanceID','type':'string','readonly':'true()','calculate':"concat('uuid:', uuid())"})
out=Path(__file__).parent/'meeting-native/nsipa_registry_household.xml';E.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True);print('Native household offline form generated.')
