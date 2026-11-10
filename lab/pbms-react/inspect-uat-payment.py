import json,pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/verify-api.py').read_text().split('checks=[]')[0])
fixtures=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json').read_text())
for fixture in fixtures:
    if 'disbursement_list_id' not in fixture:continue
    id=fixture['disbursement_list_id'];headers={'Origin':BASE}
    response=session.post(BASE+'/pbms-ui-api/workflow/'+str(id),json={},headers=headers,timeout=60);data=response.json()
    print('List',id,'status',response.status_code,'batches',data.get('batches'))
    for b in data.get('batches',[]):
        r=session.post(BASE+'/pbms-ui-api/payment/'+str(id),json={'kind':'batch','reference':b['batch_id']},headers=headers,timeout=60)
        print('Report',r.status_code,{k:v for k,v in r.json().items() if 'status' in k or 'error' in k})
