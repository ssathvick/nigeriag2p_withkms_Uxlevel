import pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
call('ir.module.module','update_list',[])
ids=call('ir.module.module','search',[[['name','=','nsipa_approval']]])
state=call('ir.module.module','read',[ids],{'fields':['state']})[0]['state']
call('ir.module.module','button_immediate_upgrade' if state=='installed' else 'button_immediate_install',[ids])
print('Native module installed')
