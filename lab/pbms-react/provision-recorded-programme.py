import pathlib,json
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
ids=call('g2p.program.definition','search',[[['program_mnemonic','=','NSIPA Household Support November 2026']]])
assert len(ids)==1
credentials=json.loads(pathlib.Path('/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json').read_text())
for key,role in [('admin','Programme Admin'),('payment','Payment'),('finance','Finance'),('audit','Audit'),('ceo','CEO')]:
 call('g2p.program.definition','nsipa_assign_role',[ids,credentials[key]['uid'],role])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/recorded-demo.json').write_text(json.dumps({'program_id':ids[0],'program_name':'NSIPA Household Support November 2026'}))
print('Existing five staff accounts assigned to the newly created programme. No approval decisions or lists changed.')
