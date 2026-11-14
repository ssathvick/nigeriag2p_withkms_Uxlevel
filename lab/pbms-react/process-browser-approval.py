import pathlib,json,sys
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
if len(sys.argv)>1:
 p=int(sys.argv[1]);creds=json.loads(pathlib.Path('/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json').read_text())
 assert call('g2p.program.definition','read',[[p]],{'fields':['program_mnemonic']})[0]['program_mnemonic'].startswith('NSIPA_BROWSER_')
 for k,r in [('payment','Payment'),('finance','Finance'),('audit','Audit'),('ceo','CEO')]:call('g2p.program.definition','nsipa_assign_role',[[p],creds[k]['uid'],r])
cron=call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['name','=','process_lists']]],{'fields':['res_id']})[0]['res_id']
call('ir.cron','method_direct_trigger',[[cron]])
print('Staff membership assigned and pending lists processed by the native scheduled action.')
