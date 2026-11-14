import pathlib,json,time,datetime
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
p=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-approval-results.json').read_text())['program_id']
call('g2p.program.definition','write',[[p],{'program_status':'ACTIVE'}])
e=call('g2p.enrollment.cycle','create',[{'program_id':p,'cycle_number':5,'enrollment_start_date':'2026-11-01','enrollment_end_date':'2026-11-12','disbursement_start_date':'2027-02-01','disbursement_end_date':'2027-02-28'}])
l=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':e,'mnemonic':'NSIPA_SCHEDULED_WORKER_'+str(e)}])
print('Pending list created; waiting for the automatic scheduled worker.',flush=True)
started=time.monotonic()
while time.monotonic()-started<90:
 r=call('g2p.beneficiary.list','read',[[l]],{'fields':['nsipa_status','nsipa_error']})[0]
 if r['nsipa_status']=='complete':
  result={'status':'passed','check':'automatic scheduled processing without a manual trigger','elapsed_seconds':round(time.monotonic()-started,1),'list_id':l}
  pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-scheduled-worker.json').write_text(json.dumps(result,indent=2));print('PASS automatic scheduled worker completed the list.',flush=True);break
 if r['nsipa_status']=='error':raise AssertionError(r['nsipa_error'])
 time.sleep(3)
else:raise AssertionError('Scheduled worker did not complete the list within 90 seconds.')
call('g2p.program.definition','write',[[p],{'program_status':'PAUSED'}])
