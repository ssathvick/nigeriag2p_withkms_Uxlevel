import os,pathlib,json,time,requests
r=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react');f=json.loads((r/'evidence/connected-payments/fixture.json').read_text());c=json.loads(pathlib.Path(os.environ.get('PBMS_APPROVAL_ACCOUNTS_FILE','/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json')).read_text())['payment']
origin='https://g2p-pbms.wverve.in';s=requests.Session()
a=s.post(origin+'/web/session/authenticate',json={'jsonrpc':'2.0','method':'call','params':{'db':'pbmsdb','login':c['login'],'password':c['password']},'id':1},timeout=30).json();assert a.get('result',{}).get('uid')
def api(path,data=None):
 p=s.post(origin+'/pbms-ui-api/'+path,json=data or {},headers={'Origin':origin},timeout=45);assert p.status_code in [200,202],(path,p.status_code,p.text[:250]);return p.json()
for i in range(90):
 d=api('workflow/'+str(f['list_id']))
 if d['batches'] and d['envelopes']:
  assert len(d['batches'])==len(d['envelopes'])==1
  batch=api('payment/'+str(f['list_id']),{'kind':'batch','reference':d['batches'][0]['batch_id']})
  envelope=api('payment/'+str(f['list_id']),{'kind':'envelope','reference':d['envelopes'][0]['disbursement_envelope_id']})
  if batch.get('sponsor_bank_dispatch_status')=='PROCESSED' and envelope.get('number_of_disbursements_reconciled')==1:break
 if i%10==0:print('Waiting for connected simulator reconciliation',flush=True)
 time.sleep(3)
assert batch.get('fa_resolution_status')=='PROCESSED' and batch.get('sponsor_bank_dispatch_status')=='PROCESSED'
assert envelope.get('number_of_disbursements_reconciled')==1
assert d['batches'][0]['total_disbursement_quantity']==1.0 and d['batches'][0]['number_of_beneficiaries']==1
assert not d['permissions']['approve'] and not d['permissions']['verify']
bad=s.post(origin+'/pbms-ui-api/payment/'+str(f['list_id']),json={'kind':'batch','reference':'unrelated'},headers={'Origin':origin},timeout=30);assert bad.status_code==403
result={'status':'passed','same_approved_list_id':f['list_id'],'beneficiaries':1,'ngn':1.0,'envelopes':1,'batches':1,'financial_address_resolution':batch['fa_resolution_status'],'local_simulator_dispatch':batch['sponsor_bank_dispatch_status'],'reconciled':1,'separate_approval_disabled':True,'unrelated_report_blocked':True}
(r/'evidence/connected-payments/payment-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
