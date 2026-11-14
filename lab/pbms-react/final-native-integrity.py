import pathlib,subprocess,hashlib,json
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react')
local=(root/'nsipa_approval/models.py').read_bytes();live=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/pbms-odoo','--','cat','/opt/odoo/extraaddons/openg2p-pbms/nsipa_approval/models.py'])
assert local.decode().replace('\r\n','\n')==live.decode().replace('\r\n','\n')
exec((root.parent/'inspect-pbms-react.py').read_text().split('models =')[0])
assert call('ir.module.module','search_count',[[['name','=','nsipa_approval'],['state','=','installed']]])==1
assert call('ir.rule','search_count',[[['name','like','NSIPA']]])>=4
presentation=json.loads((root/'evidence/presentation-program.json').read_text())['program_id']
p=call('g2p.program.definition','nsipa_workspace',[[presentation]])
assert p['program']['program_status']=='ACTIVE' and p['program']['nsipa_setup_ready'] and len(p['members'])==5
assert not p['lists']
print('PASS installed addon source integrity, programme-scoped record rules and ready presentation programme with five staff accounts.')
