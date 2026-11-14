import test_meeting_native_workflow as t
from test_mbr_db_connection import connect
main=t.state['cases']['Return then approve']
def get(cr):return t.call('aarin@gmail.com','change-request/get',{'change_request_id':cr['id']})[0]
def create(value):
 with connect() as c:
  with c.cursor() as q:q.execute("SELECT tab_id FROM g2p_register_ui_tab_sections WHERE section_id='hh_dwelling_services' LIMIT 1");tab=q.fetchone()[0]
 body={'register_id':t.REG,'register_mnemonic':'Household','section_register_id':t.REG,'tab_id':tab,'section_id':'hh_dwelling_services','internal_record_id':main['internal_id'],'edit_action':'UPDATE','section_records':[{'internal_record_id':main['internal_id'],'edit_action':'UPDATE','rooms_count':value}]}
 result,_=t.call('aarin@gmail.com','change-request/create',body);return result,body
def current_value():
 with connect() as c:
  with c.cursor() as q:q.execute('SELECT rooms_count FROM g2p_register_households WHERE internal_record_id=%s',(main['internal_id'],));return q.fetchone()[0]
cr=t.state['cases'].get('Master change')
if not cr:
 result,body=create(2);cr={'id':result['change_request_id'],'body':body};t.state['cases']['Master change']=cr;t.save()
cr['request_id']=get(cr)['awe_request_id'];t.save()
if not cr.get('returned'):
 t.decide(cr,'abutu@gmail.com','return','Correct this fictional housing change, then resubmit.',kind='registry.change_request')
 t.wait_for(lambda:str(get(cr).get('awe_request_status_summary')).startswith('returned'),'Returned master change')
 cr['returned']=True;t.save()
t.check('Returned change request retains its proposal and review history',any(e['event_type']=='request_returned' for e in get(cr).get('review_history',[])))
if not cr.get('resubmitted'):
 result,_=t.call('aarin@gmail.com','change-request/create',cr['body']);t.check('Corrected master change reuses original request ID',result['change_request_id']==cr['id']);cr['resubmitted']=True;cr['request_id']=get(cr)['awe_request_id'];t.save()
if not cr.get('level1'):
 t.decide(cr,'abutu@gmail.com','approve','First review of corrected optional section.',kind='registry.change_request')
 t.wait_for(lambda:'stage2' in str(get(cr).get('awe_request_status_summary')),'Master change stage 2');t.check('First reviewer does not apply master change',current_value()!=2);cr['level1']=True;t.save()
if not cr.get('approved'):
 t.decide(cr,'adaku@gmail.com','approve','Independent master change approval.',stage=2,kind='registry.change_request')
 t.wait_for(lambda:current_value()==2,'Master change applied');cr['approved']=True;t.save()
t.check('Second reviewer applies only approved section changes',current_value()==2)
with connect() as c:
 with c.cursor() as q:q.execute('SELECT count(*) FROM g2p_register_history_households WHERE change_request_id=%s',(cr['id'],));t.check('Approved master change creates native version history',q.fetchone()[0]>0)
result,status=t.call('admin@openg2p.org','intake-form/save-intake-form-submission',{'submission_id':None,'form_id':t.FORM,'register_id':t.REG,'section_id':'hh_composition_headship','section_register_id':t.REG,'section_payload':[main['payload']]},False)
t.check('Administrator capture is blocked by backend authorization',status==403)
result,status=t.call('abutu@gmail.com','intake-form/save-intake-form-submission',{'submission_id':None,'form_id':t.FORM,'register_id':t.REG,'section_id':'hh_composition_headship','section_register_id':t.REG,'section_payload':[main['payload']]},False)
t.check('Reviewer capture is blocked by backend authorization',status==403)
print('Native master change workflow passed.')
