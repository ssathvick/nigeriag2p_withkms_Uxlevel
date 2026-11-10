import datetime,json,pathlib,time,requests
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
fixture=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json').read_text())[0]
program=fixture['program_id'];keys=['auto_approve_disbursement','verifications_for_disbursement']
prior=call('g2p.program.definition','read',[[program]],{'fields':keys})[0]
origin='https://'+fixture['host'];s=requests.Session()
s.post(origin+'/web/session/authenticate',json={'jsonrpc':'2.0','method':'call','params':{'db':'pbmsdb','login':'admin@nigeria.openg2p.localhost','password':password},'id':1},timeout=30).raise_for_status()
def api(path,data=None):
    r=s.post(origin+'/pbms-ui-api/'+path,json=data or {},headers={'Origin':origin},timeout=60);r.raise_for_status();return r.json()
try:
    call('g2p.program.definition','write',[[program],{'auto_approve_disbursement':True,'verifications_for_disbursement':0}])
    tag=fixture['tag']+'_AUTO_'+str(int(time.time()))
    cycle=call('g2p.disbursement.cycle','create',[{'program_id':program,'cycle_mnemonic':tag,'disbursement_schedule_date':str(datetime.date.today())}])
    listing=call('g2p.beneficiary.list','create',[{'disbursement_cycle_id':cycle,'mnemonic':tag,'brief':'Automatic-policy UAT; same single fictional beneficiary; NGN 1; existing local simulator only.'}])
    print('Automatic payment fixture',listing,flush=True)
    for n in range(120):
        data=api('workflow/'+str(listing))
        if data['batches']:
            report=api('payment/'+str(listing),{'kind':'batch','reference':data['batches'][0]['batch_id']})
            if report.get('sponsor_bank_dispatch_status')=='PROCESSED':break
        if n%15==0:print('Automatic policy progress:',data['list']['list_workflow_status'],data['list']['disbursement_batch_creation_status'],flush=True)
        time.sleep(3)
    assert data['readiness']['approved'] and data['readiness']['required']==0
    assert len(data['batches'])==1 and data['batches'][0]['total_disbursement_quantity']==1
    assert report['sponsor_bank_dispatch_status']=='PROCESSED'
    result={'automatic_payment':'passed','backend_method':'approve_for_disbursement','list_id':listing,'simulated_quantity_ngn':1,'simulator_dispatch':'PROCESSED','policy_restored':True}
finally:
    call('g2p.program.definition','write',[[program],{k:prior[k] for k in keys}])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/auto-payment-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
