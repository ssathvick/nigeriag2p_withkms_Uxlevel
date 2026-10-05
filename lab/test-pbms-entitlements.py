exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/test-pbms-enrollment.py').read().split('program=')[0])
program=call('g2p.program.definition','search',[[['program_mnemonic','=','NG_LAB_FARMER']]])[0]
enrol=call('g2p.beneficiary.list','search',[[['mnemonic','=','NG_LAB_ELIGIBILITY_TEST']]])[0]
assert call('g2p.beneficiary.list','read',[[enrol]],{'fields':['eligibility_process_status']})[0]['eligibility_process_status']=='complete'
call('g2p.beneficiary.list','write',[[enrol],{'list_workflow_status':'approved_final_enrolment','approval_date':'2026-10-03','eligibility_latest_error_code':False}])
cycle=upsert('g2p.disbursement.cycle',[['cycle_mnemonic','=','NG_LAB_DISBURSEMENT_001']],{'cycle_mnemonic':'NG_LAB_DISBURSEMENT_001','program_id':program,'disbursement_schedule_date':'2026-10-03'})
listing=upsert('g2p.beneficiary.list',[['mnemonic','=','NG_LAB_ENTITLEMENT_TEST']],{'mnemonic':'NG_LAB_ENTITLEMENT_TEST','disbursement_cycle_id':cycle,'brief':'Synthetic 25000 NGN benefit calculation; no live payments.','eligibility_process_status':'pending'})
print('Synthetic disbursement entitlement list prepared:',listing)
