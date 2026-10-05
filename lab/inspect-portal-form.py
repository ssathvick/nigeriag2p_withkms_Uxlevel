exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/bootstrap-portal.py').read().split("call('ir.module.module','update_list'")[0])
print(call('formio.version','fields_get',[],{'attributes':['type','required','selection','relation']}))
print(call('formio.version','search_read',[[]]))
