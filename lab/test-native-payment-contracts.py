"""Validate one million synthetic instructions with installed native models, not payments."""
import json,subprocess,sys
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
base=r.svc('openg2p-g2p-bridge-example-bank-api');schema=requests.get(base+'/openapi.json',timeout=10).json()['components']['schemas']
assert schema['BlockFundsRequest']['properties']['amount'].get('exclusiveMinimum')==0
control=requests.post(base+'/check_funds',json={'account_number':'PHASE1-DEMO-TREASURY','account_currency':'NGN','total_funds_needed':1},timeout=10);print('Positive read-only funds control',control.status_code,control.json().get('status'));assert control.status_code==200 and control.json().get('status') in ('success','SUCCESS')
negative=[]
for path,body,field in [('/check_funds',{'account_number':'PHASE1-DEMO-TREASURY','account_currency':'NGN'},'total_funds_needed'),('/block_funds',{'account_number':'PHASE1-DEMO-TREASURY','currency':'NGN'},'amount')]:
 for value in [-1,0]:
  resp=requests.post(base+path,json={**body,field:value},timeout=10);negative.append({'path':path,'value':value,'http_status':resp.status_code});print('Rejected amount check',path,value,resp.status_code);assert resp.status_code in (400,422)
script='''import json,time
from pydantic import ValidationError
from openg2p_example_bank_models.schemas.payment_request import InitiatePaymentPayload
base={'payment_reference_number':'PHASE1-LOAD-0','remitting_account':'PHASE1-DEMO-TREASURY','remitting_account_currency':'NGN','payment_amount':1,'funds_blocked_reference_number':'PHASE1-NOT-DISPATCHED','beneficiary_name':'Fictional capacity record','beneficiary_account':'LAB-LOAD-0','beneficiary_account_currency':'NGN','beneficiary_account_type':'BANK_ACCOUNT','beneficiary_bank_code':'EXAMPLE_BANK','beneficiary_branch_code':'LAB','payment_date':'2026-10-12'}
for amount in [-1,0,float('inf'),float('nan')]:
 try:InitiatePaymentPayload(**{**base,'payment_amount':amount})
 except ValidationError:pass
 else:raise AssertionError('Invalid amount accepted')
start=time.perf_counter();count=0
for i in range(1000000):
 item=InitiatePaymentPayload(**{**base,'payment_reference_number':'PHASE1-LOAD-'+str(i),'beneficiary_account':'LAB-LOAD-'+str(i)})
 assert item.payment_amount==1;count+=1
print('PHASE1_RESULT:'+json.dumps({'validated_instructions':count,'seconds':round(time.perf_counter()-start,3),'invalid_amount_checks':4}))
'''
run=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/openg2p-g2p-bridge-example-bank-api','--','python','-'],input=script,text=True,capture_output=True,timeout=120)
log=r.ROOT/'phase1-private-tests/native-payment-contracts.log';log.write_text(run.stdout+run.stderr);log.chmod(0o600);assert run.returncode==0
result=json.loads(next(x.split('PHASE1_RESULT:',1)[1] for x in run.stdout.splitlines() if x.startswith('PHASE1_RESULT:')))
report={'scope':'Installed native bank model validation of 1M instructions; no dispatch or settlement','validation':result,'native_api_negative_checks':negative,'status':'passed_contract_validation_only','million_native_settlement_batch':'Not run','limitations':['No funds blocked, ledger records created or payments issued','Does not establish 1M end-to-end batch throughput, routing success or reconciliation targets']}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-payment-contract-capacity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
