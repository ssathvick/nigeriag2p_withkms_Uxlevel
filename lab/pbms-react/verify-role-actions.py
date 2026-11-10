import datetime,json,pathlib,secrets,time,requests
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
fixtures=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json').read_text())
def group(module,name):return call('ir.model.data','search_read',[[['module','=',module],['name','=',name]]],{'fields':['res_id']})[0]['res_id']
base=group('base','group_user');created=[];results=[]
try:
    for fixture in fixtures:
        origin='https://'+fixture['host'];assignment=call('res.groups','search',[[['name','=',fixture['tag']]]])[0]
        sessions={};ids={}
        for role,groupname in [('verifier','group_enrolment_verification'),('approver','group_enrolment_approval')]:
            task_password=secrets.token_urlsafe(24);login='react-uat-'+role+'-'+secrets.token_hex(4)+'@example.invalid'
            groups=[base,group('g2p_pbms',groupname),assignment]
            if role=='verifier':groups+=call('res.groups','search',[[['name','=','Document Write']]])
            user=call('res.users','create',[{'name':'React UAT '+role,'login':login,'password':task_password,'groups_id':[[6,0,groups]]}],{'context':{'no_reset_password':True}});created.append(user);ids[role]=user
            s=requests.Session();r=s.post(origin+'/web/session/authenticate',json={'jsonrpc':'2.0','method':'call','params':{'db':'pbmsdb','login':login,'password':task_password},'id':1},timeout=30);assert r.json().get('result',{}).get('uid')==user;sessions[role]=s
        listing=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':fixture['enrollment_cycle_id'],'mnemonic':fixture['tag']+'_ROLES_'+secrets.token_hex(3),'brief':'Isolated React role verification test. No payment.'}])
        print(fixture['host'],'waiting for role-test calculation',listing,flush=True)
        for _ in range(90):
            row=call('g2p.beneficiary.list','read',[[listing]],{'fields':['eligibility_process_status']})[0]
            if row['eligibility_process_status']=='complete':break
            time.sleep(2)
        assert row['eligibility_process_status']=='complete'
        def api(role,path,body=None):return sessions[role].post(origin+'/pbms-ui-api/'+path,json=body or {},headers={'Origin':origin},timeout=60)
        workflow=api('verifier','workflow/'+str(listing));assert workflow.status_code==200,workflow.text
        assert workflow.json()['permissions']=={'verify':True,'approve':False}
        assert api('approver','approve/'+str(listing)).status_code==409
        assert api('verifier','approve/'+str(listing)).status_code==403
        assert api('approver','verification/'+str(listing),{'comment':'Must not persist'}).status_code==403
        verification=api('verifier','verification/'+str(listing),{'comment':'Synthetic UAT verified by a dedicated verification role.'});assert verification.status_code==200,verification.text
        stored=call('storage.file','read',[[verification.json()['id']]],{'fields':['verified_by','beneficiary_list_id']})[0];assert stored['verified_by'][0]==ids['verifier'] and stored['beneficiary_list_id'][0]==listing
        approval=api('approver','approve/'+str(listing));assert approval.status_code==200,approval.text
        assert approval.json()['status']=='approved_final_enrolment'
        results.append({'host':fixture['host'],'list_id':listing,'dedicated_verifier':'passed','dedicated_approver':'passed','separation_of_duties':'passed','evidence_author':'correct'})
        print('PASS',fixture['host'],'dedicated verification and approval roles',flush=True)
finally:
    for user in created:call('res.users','write',[[user],{'active':False}])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/role-action-results.json').write_text(json.dumps(results,indent=2))
