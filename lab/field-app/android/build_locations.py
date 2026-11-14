import json,base64,collections,pathlib
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/field-app/android')
flat=json.loads(base64.b64decode(json.load(open('/tmp/ng2p-api.json'))['content']))['data']
wards=json.loads(base64.b64decode(json.load(open('/tmp/ng2p-wards-blob.json'))['content']))
assert len(flat)==811 and len(wards)==8799
s=[{'id':x['id'],'name':x['name']['en']} for x in flat if x['level']==1]
l=[{'id':x['id'],'name':x['name']['en'],'parent':x['parent']['id']} for x in flat if x['level']==2]
w=[{'id':x['id'],'name':x['name']['en'],'parent':x['parent']['id']} for x in wards]
assert len({x['id'] for x in s})==37 and len({x['id'] for x in l})==774 and len({x['id'] for x in w})==8799
assert all(x['parent'] in {y['id'] for y in s} for x in l)
assert all(x['parent'] in {y['id'] for y in l} for x in w)
(root/'assets').mkdir(exist_ok=True)
(root/'assets/locations.json').write_text(json.dumps({'states':s,'lgas':l,'wards':w},ensure_ascii=False,separators=(',',':')),encoding='utf8')
print('Catalog:',len(s),'states/FCT,',len(l),'LGAs,',len(w),'wards')
