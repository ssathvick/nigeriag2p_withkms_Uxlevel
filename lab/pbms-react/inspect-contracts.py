import json,pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
models=call('ir.model','search_read',[[['model','like','g2p.%']]],{'fields':['model','name']})
out={}
for m in models+[{'model':'storage.file'}]:
    name=m['model']
    out[name]={'fields':call(name,'fields_get',[],{'attributes':['string','type','relation','required','readonly','selection','help','store']})}
    try:out[name]['view']=call(name,'get_view',[],{'view_type':'form'})
    except Exception:pass
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/contracts.json').write_text(json.dumps(out,indent=2))
print('Exported',len(out),'model contracts; no record data.')
