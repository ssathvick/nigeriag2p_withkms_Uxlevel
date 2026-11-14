"""Prepare one actual rejected monthly list for correction-screen validation."""
import pathlib,json
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
creds=json.loads(pathlib.Path('/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json').read_text())
s=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-approval-results.json').read_text());p=s['program_id']
call('g2p.program.definition','write',[[p],{'program_status':'ACTIVE'}])
en=call('g2p.enrollment.cycle','create',[{'program_id':p,'cycle_number':2,'enrollment_start_date':'2026-11-01','enrollment_end_date':'2026-11-12','disbursement_start_date':'2026-12-01','disbursement_end_date':'2026-12-28'}])
el=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':en,'mnemonic':'NSIPA_CORRECTION_ENR_'+str(en)}])
cron=call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['name','=','process_lists']]],{'fields':['res_id']})[0]['res_id'];call('ir.cron','method_direct_trigger',[[cron]])
dc=call('g2p.disbursement.cycle','create',[{'program_id':p,'cycle_mnemonic':'NSIPA_CORRECTION_DEC_'+str(en),'nsipa_enrollment_cycle_id':en,'disbursement_schedule_date':'2026-12-20'}])
dl=call('g2p.beneficiary.list','create',[{'disbursement_cycle_id':dc,'mnemonic':'NSIPA_CORRECTION_LIST_'+str(en)}]);call('ir.cron','method_direct_trigger',[[cron]])
for key,r in [('admin','Programme Admin'),('payment','Payment'),('finance','Finance'),('audit','Audit'),('ceo','CEO')]:call('g2p.program.definition','nsipa_assign_role',[[p],creds[key]['uid'],r])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/correction-ui-fixture.json').write_text(json.dumps({'program_id':p,'list_id':dl}))
print('Correction fixture ready')
