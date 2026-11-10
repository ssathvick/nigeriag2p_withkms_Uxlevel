import json,pathlib,time,requests
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
fixture=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json').read_text())[0]
program=fixture['program_id'];keys=['auto_approve_enrolment','verifications_for_enrolment']
prior=call('g2p.program.definition','read',[[program]],{'fields':keys})[0]
try:
    call('g2p.program.definition','write',[[program],{'auto_approve_enrolment':True,'verifications_for_enrolment':0}])
    listing=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':fixture['enrollment_cycle_id'],'mnemonic':fixture['tag']+'_AUTO_'+str(int(time.time())),'brief':'Synthetic automatic-enrollment policy test; no payment.'}])
    for _ in range(90):
        row=call('g2p.beneficiary.list','read',[[listing]],{'fields':['eligibility_process_status']})[0]
        if row['eligibility_process_status']=='complete':break
        time.sleep(2)
    assert row['eligibility_process_status']=='complete'
    origin='https://'+fixture['host'];s=requests.Session()
    s.post(origin+'/web/session/authenticate',json={'jsonrpc':'2.0','method':'call','params':{'db':'pbmsdb','login':'admin@nigeria.openg2p.localhost','password':password},'id':1},timeout=30).raise_for_status()
    response=s.post(origin+'/pbms-ui-api/workflow/'+str(listing),json={},headers={'Origin':origin},timeout=60)
    assert response.status_code==200,response.text
    data=response.json();assert data['readiness']['approved'] and data['readiness']['required']==0
    result={'automatic_enrollment':'passed','backend_policy':'existing action_open_summary_wizard','list_id':listing,'policy_restored':True}
finally:
    call('g2p.program.definition','write',[[program],{k:prior[k] for k in keys}])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/auto-policy-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
