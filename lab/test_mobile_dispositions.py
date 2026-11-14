import sys,json,uuid,time,xml.etree.ElementTree as E
from pathlib import Path
import yaml,requests
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'client-concerns'))
from test_location_import_e2e import login
from test_mbr_db_connection import connect
from test_meeting_native_workflow import call,REG,FORM,detail,master,tasks,wait_for,decide
OUT=ROOT.parent/'output/mobile-disposition-verification';OUT.mkdir(exist_ok=True)
PRIVATE=Path('/opt/openg2p-lab/registration/mobile-disposition-evidence');PRIVATE.mkdir(mode=0o700,exist_ok=True)
phase=sys.argv[1]
def load(name):return json.loads((OUT/(name+'.json')).read_text())
def save(name,s):(OUT/(name+'.json')).write_text(json.dumps(s,indent=2,default=str))
def check(name,s,text):
 if text not in s['checks']:s['checks'].append(text)
 save(name,s);print('PASS '+name+': '+text,flush=True)
def row(s,prefix='g2p_intake_form_'):
 with connect() as c:
  with c.cursor() as q:
   q.execute('SELECT row_to_json(h) FROM '+prefix+'households h WHERE internal_record_id=%s',(s['internal_id'],));h=q.fetchone()[0]
   q.execute('SELECT row_to_json(i) FROM '+prefix+'individuals i WHERE link_internal_record_id=%s',(s['internal_id'],));m=[r[0] for r in q.fetchall()]
 return h,m
def preserved(name,s,prefix='g2p_intake_form_'):
 h,m=row(s,prefix);base=json.loads((PRIVATE/(name+'-baseline.json')).read_text());fields=['internal_record_id','household_head_internal_record_id','sponsor_name','consent_status','latitude','longitude','location_accuracy_m','location_captured_at','geo_lowest_level_value_id','income_source','monthly_household_income','shock_types','crops_grown','television_count','rooms_count']
 assert all(h.get(k)==base['household'].get(k) for k in fields),'Household data changed'
 assert len(m)==len(base['members'])==1
 for k in ['internal_record_id','link_internal_record_id','first_name','last_name','estimated_age','relationship_to_head']:assert m[0].get(k)==base['members'][0].get(k),'Member changed: '+k
 return h,m
if phase=='prepare':
 password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];admin=login('https://g2p-odk.wverve.in','admin',password,True);r=admin.get('https://g2p-odk.wverve.in/v1/projects/1/app-users',timeout=30);r.raise_for_status();account=next(a for a in r.json() if a['displayName']=='Registry field capture · abuchi@gmail.com')
 for name in (sys.argv[2:] or ['returned','rejected']):
  file=OUT/(name+'.json');s=load(name) if file.exists() else {'checks':[],'instance':'uuid:'+str(uuid.uuid4()),'record_name':'Meeting Verification Mobile '+('Return and Resubmission' if name=='returned' else 'Permanent Rejection at Level 2' if name=='rejected-level2' else 'Permanent Rejection')}
  s['internal_id']=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-native-odk:'+s['instance']));s['source']='Previous physical Android interview replayed with a fresh UUID through authenticated mobile ingestion; no new phone capture claimed';save(name,s)
  if not s.get('uploaded'):
   data=E.parse('/opt/openg2p-lab/registration/household-final-e2e-private-evidence/physical-final.xml').getroot();data.find('meta/instanceID').text=s['instance'];data.find('household/record_name').text=s['record_name'];r=requests.post('https://g2p-odk.wverve.in/v1/key/'+account['token']+'/projects/1/submission',files={'xml_submission_file':('submission.xml',E.tostring(data),'text/xml')},headers={'X-OpenRosa-Version':'1.0'},verify='/opt/openg2p-lab/registration/ca-bundle.crt',timeout=45);assert r.status_code in [201,202],r.status_code;s['uploaded']=True;save(name,s)
  for _ in range(40):
   with connect() as c:
    with c.cursor() as q:q.execute('SELECT submission_id FROM g2p_intake_form_households WHERE internal_record_id=%s',(s['internal_id'],));found=q.fetchone()
   if found:s['id']=str(found[0]);save(name,s);break
   time.sleep(2)
  assert s.get('id');assert detail(s)['approval_status']=='PENDING' and not master(s)
  h,m=row(s);p=PRIVATE/(name+'-baseline.json')
  if not p.exists():p.write_text(json.dumps({'household':h,'members':m}));p.chmod(0o600)
  check(name,s,'Mobile-origin submission automatically enters native review')
else:
 name='rejected-level2' if phase.startswith('rejected-level2') else 'rejected' if phase=='rejected' else 'returned';s=load(name)
 if phase=='returned':
  d=wait_for(lambda:detail(s) if detail(s)['draft_status']=='DRAFT' else None,'Editable returned intake');assert d['approval_status']=='PENDING' and str(d['awe_request_status_summary']).startswith('returned');s['return_count']=sum(e['event_type']=='request_returned' for e in d.get('review_history',[]));assert s['return_count']>=1;s['correction_expected']='Fictional community corrected after mobile review' if s['return_count']==1 else 'Fictional community corrected after second review';assert not master(s);preserved(name,s);s['returned']=True;check(name,s,'Return retains history and opens the same intake for correction without publishing')
 elif phase=='resubmitted':
  d=detail(s);assert d['draft_status']=='FINAL' and d['approval_status']=='PENDING';assert any(e['event_type']=='request_returned' for e in d.get('review_history',[]));h,m=preserved(name,s);assert h['survey_community']==s['correction_expected'];assert not master(s);assert any(t['stage_order']==1 and t['status']=='open' for t in tasks(s));s['resubmitted']=True;check(name,s,'UI correction and resubmission retain submission/member identity, GPS and survey values')
 elif phase in ['level1','rejected-level2-l1']:
  wait_for(lambda:any(t['stage_order']==2 and t['status']=='open' for t in tasks(s)),'Second review');assert not master(s);check(name,s,'Resubmitted mobile intake requires first approval before second review')
 elif phase=='level2':
  wait_for(lambda:master(s),'Publication');d=detail(s);assert d['approval_status']=='APPROVED';s['review_history']=d.get('review_history',[]);assert sum(e['event_type']=='request_returned' for e in s['review_history'])==2;assert any(e['event_type']=='request_approved' for e in s['review_history']);h,m=preserved(name,s,'g2p_register_');assert h['survey_community']==s['correction_expected'] and h['functional_record_id'] and m[0]['functional_record_id'];s['status']='passed';check(name,s,'Corrected mobile household publishes only after both independent approvals')
 elif phase in ['rejected','rejected-level2']:
  wait_for(lambda:detail(s)['approval_status']=='REJECTED','Permanent rejection');assert detail(s)['draft_status']=='FINAL' and not master(s)
  for endpoint,payload in [('save-intake-form-submission',{'submission_id':s['id'],'register_id':REG,'form_id':FORM,'section_id':'hh_survey_consent','section_register_id':REG,'section_payload':[{'internal_record_id':s['internal_id'],'edit_action':'UPDATE','survey_community':'Forbidden edit regression'}]}),('finalize-intake-form-submission',{'submission_id':s['id'],'register_id':REG,'form_id':FORM})]:
   body,status=call('aarin@gmail.com','intake-form/'+endpoint,payload,expect=False);assert status>=400 or body.get('error'),endpoint
  preserved(name,s);d=detail(s);assert d['approval_status']=='REJECTED' and not master(s);s['review_history']=d.get('review_history',[]);assert any(e['event_type']=='request_rejected' for e in s['review_history']);s['status']='passed';check(name,s,'Permanent rejection stays final, preserves its reason/history, blocks edits and resubmission, and never publishes')
 else:raise ValueError(phase)
 save(name,s)
