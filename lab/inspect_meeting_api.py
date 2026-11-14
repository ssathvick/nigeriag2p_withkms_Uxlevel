import test_meeting_native_workflow as t
case=t.state['cases']['Return then approve']
response=t.session('aarin@gmail.com').get(t.HOST+'/api/stats/tasks');print('stats',response.status_code,response.text[:300])
print('Detail request',t.detail(case)['awe_request_id'])
for email in ['abutu@gmail.com','adaku@gmail.com']:
 result,_=t.call(email,'awe/tasks-for-request',{'request_id':t.detail(case)['awe_request_id']});print(email,[(x['stage_order'],x['assignee'],x['status']) for x in result['tasks']])
