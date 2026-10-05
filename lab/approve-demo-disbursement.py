exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/test-pbms-enrollment.py').read().split('program=')[0])
listing=call('g2p.beneficiary.list','search',[[['mnemonic','=','NG_LAB_ENTITLEMENT_TEST']]])[0]
row=call('g2p.beneficiary.list','read',[[listing]],{'fields':['eligibility_process_status','entitlement_process_status','number_of_registrants','number_of_entitlements_processed']})[0]
print('Demo calculation:',row)
assert row['eligibility_process_status']=='complete' and row['entitlement_process_status']=='complete'
call('g2p.beneficiary.list','write',[[listing],{'list_workflow_status':'approved_for_disbursement','approval_date':'2026-10-03','envelope_creation_status':'pending','envelope_creation_number_of_attempts':0}])
cycle=call('g2p.disbursement.cycle','search',[[['cycle_mnemonic','=','NG_LAB_DISBURSEMENT_001']]])[0]
call('g2p.disbursement.cycle','write',[[cycle],{'approved_for_disbursement':True}])
print('Approved synthetic demo for local Bridge simulator processing.')
