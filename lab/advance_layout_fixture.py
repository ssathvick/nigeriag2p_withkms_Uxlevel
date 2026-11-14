import json,sys
from pathlib import Path
from test_meeting_native_workflow import call,decide,wait_for,detail,tasks,master,REG
from test_mbr_db_connection import connect
path=Path(__file__).parent.parent/'output/registry-layout-approval-fixture/workflow.json';s=json.loads(path.read_text());action=sys.argv[1]
if action=='l1':
 decide(s,'abutu@gmail.com','approve','Fictional layout test: first approval reviewed.')
 wait_for(lambda:any(t['stage_order']==2 for t in tasks(s)),'Second approval');s['l1']=True
elif action=='l2':
 decide(s,'adaku@gmail.com','approve','Fictional layout test: second approval reviewed.',stage=2)
 wait_for(lambda:master(s),'Fixture publication');s['l2']=True
elif action=='change':
 with connect() as c:
  with c.cursor() as q:q.execute("SELECT tab_id FROM g2p_register_ui_tab_sections WHERE section_id='hh_dwelling_services' LIMIT 1");tab=q.fetchone()[0]
 body={'register_id':REG,'register_mnemonic':'Household','section_register_id':REG,'tab_id':tab,'section_id':'hh_dwelling_services','internal_record_id':s['internal_id'],'edit_action':'UPDATE','section_records':[{'internal_record_id':s['internal_id'],'edit_action':'UPDATE','rooms_count':2}]}
 result,_=call('aarin@gmail.com','change-request/create',body);cid=result['change_request_id'];d=call('aarin@gmail.com','change-request/get',{'change_request_id':cid})[0];s['change']={'id':cid,'request_id':d['awe_request_id']}
elif action=='change_l1':
 decide(s['change'],'abutu@gmail.com','approve','Fictional change-request layout test.',kind='registry.change_request');wait_for(lambda:any(t['stage_order']==2 for t in call('adaku@gmail.com','awe/tasks-for-request',{'request_id':s['change']['request_id']})[0]['tasks']),'Change second stage')
elif action=='finish':s['status']='passed'
else:raise ValueError('Unsupported action')
path.write_text(json.dumps(s,indent=2));print('Completed fixture step: '+action)
