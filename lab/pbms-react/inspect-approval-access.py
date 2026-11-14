import pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
print(call('ir.rule','search_read',[[['model_id.model','in',['g2p.program.definition','g2p.beneficiary.list','g2p.household.registry']]]],{'fields':['name','domain_force','groups','perm_read','perm_write']}))
print(call('res.users','search_read',[[['active','=',True],['share','=',False]]],{'fields':['login','groups_id'],'limit':12}))
