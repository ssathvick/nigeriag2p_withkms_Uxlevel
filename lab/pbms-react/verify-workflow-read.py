import pathlib,json
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/verify-api.py').read_text().split('checks=[]')[0])
for host in ['pbms.nigeriag2p.com','g2p-pbms.wverve.in']:
    BASE='https://'+host
    session=requests.Session()
    user=rpc('/web/session/authenticate',{'db':'pbmsdb','login':'admin@nigeria.openg2p.localhost','password':password})
    def api(path,body=None):
        response=session.post(BASE+'/pbms-ui-api/'+path,json=body or {},headers={'Origin':BASE},timeout=90)
        if response.status_code!=200:raise RuntimeError(str(response.status_code)+' '+response.text[:500])
        return response.json()
    data=api('workflow/2');assert data['summary'] and data['envelopes'] and data['batches']
    print(host,'summary',len(data['summary']),'envelopes',len(data['envelopes']),'batches',len(data['batches']),flush=True)
    for kind,key,field in [('batch','batches','batch_id'),('envelope','envelopes','disbursement_envelope_id')]:
        report=api('payment/2',{'kind':kind,'reference':data[key][0][field]})
        assert report
        print(kind,'report fields',list(report)[:8],flush=True)
    people=api('beneficiaries/2',{'page':1});print('Beneficiary keys',list(people),flush=True)
    denied=session.post(BASE+'/pbms-ui-api/payment/2',json={'kind':'batch','reference':'invalid'},headers={'Origin':BASE},timeout=90)
    assert denied.status_code==403
    cross=session.post(BASE+'/pbms-ui-api/approve/2',json={},headers={'Origin':'https://unrelated.invalid'},timeout=30)
    assert cross.status_code==403
    rpc('/web/session/destroy')
print('PASS: both domains, complete summary/report reads, scope binding, origin checks.')
