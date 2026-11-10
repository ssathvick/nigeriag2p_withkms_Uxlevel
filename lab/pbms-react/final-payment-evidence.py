import pathlib,json,datetime
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/verify-api.py').read_text().split('checks=[]')[0])
fixtures=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json').read_text());results=[]
for f in fixtures:
    BASE='https://'+f['host'];session=requests.Session();rpc('/web/session/authenticate',{'db':'pbmsdb','login':'admin@nigeria.openg2p.localhost','password':password})
    def api(path,data=None):
        r=session.post(BASE+'/pbms-ui-api/'+path,json=data or {},headers={'Origin':BASE},timeout=60);r.raise_for_status();return r.json()
    d=api('workflow/'+str(f['disbursement_list_id']));assert len(d['batches'])==len(d['envelopes'])==1
    batch=api('payment/'+str(f['disbursement_list_id']),{'kind':'batch','reference':d['batches'][0]['batch_id']})
    envelope=api('payment/'+str(f['disbursement_list_id']),{'kind':'envelope','reference':d['envelopes'][0]['disbursement_envelope_id']})
    assert batch['fa_resolution_status']=='PROCESSED' and batch['sponsor_bank_dispatch_status']=='PROCESSED'
    result={'host':f['host'],'list_id':f['disbursement_list_id'],'beneficiaries':d['list']['number_of_registrants'],'quantity_ngn':d['batches'][0]['total_disbursement_quantity'],'financial_address_resolution':batch['fa_resolution_status'],'simulator_bank_dispatch':batch['sponsor_bank_dispatch_status'],'reconciled':envelope.get('number_of_disbursements_reconciled'),'reversed':envelope.get('number_of_disbursements_reversed'),'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    assert result['beneficiaries']==1 and result['quantity_ngn']==1
    results.append(result);rpc('/web/session/destroy')
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/payment-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
