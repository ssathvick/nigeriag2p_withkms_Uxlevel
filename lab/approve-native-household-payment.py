"""Authorize one fictional household through native PBMS; local simulator only."""
import json,sys,datetime as dt,base64,uuid
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
job=json.loads(Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-household-payment.json').read_text())
assert job['status']=='passed_calculation' and job['actual_entitlement_ngn']==25000 and job['household_reference'].startswith('IQS-REG-HH-')
account='LAB-HH-000001';now=dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("INSERT INTO accounts(account_holder_name,account_number,account_currency,account_holder_phone,account_holder_email,book_balance,available_balance,blocked_amount,created_at,updated_at,active) SELECT 'Fictional UAT household',%s,'NGN','0000999999','phase1-household@example.invalid',0,0,0,now(),now(),true WHERE NOT EXISTS(SELECT 1 FROM accounts WHERE account_number=%s)",(account,account))
body={'request_header':{'sender_app_mnemonic':'g2p_bridge','sender_app_url':'https://bridge.openg2p.localhost','request_id':'phase1-native-household-account','request_timestamp':now},'request_body':{'request_payload':{'transaction_id':'phase1-native-household-account','update_request':[{'reference_id':str(uuid.uuid4()),'timestamp':now,'id':job['household_reference'],'name':'Fictional UAT Household','fa':{'strategy_id':5,'fa_type':'BANK','bank_name':'Local Example Bank Simulator','bank_code':'EXAMPLE_BANK','branch_name':'Synthetic branch','branch_code':'LAB','account_number':account}}]}}}
encoded=base64.urlsafe_b64encode(json.dumps(body,separators=(',',':'),sort_keys=True).encode()).decode().rstrip('=')
response=requests.post(r.svc('commons-services-keymanager')+'/v1/keymanager/jwtSign',json={'id':'phase1-sandbox','version':'1.0','requesttime':now,'request':{'applicationId':'OPENG2P_BRIDGE','referenceId':'','dataToSign':encoded,'includePayload':True,'includeCertificate':False,'includeCertHash':False}},timeout=20);response.raise_for_status()
response=requests.post(r.svc('spar-openg2p-spar-mapper-api')+'/mapper/update',json=body,headers={'Signature':response.json()['response']['jwtSignedData']},timeout=20);response.raise_for_status();data=response.json();assert data['response_header']['response_status']=='SUCCESS'
updates=data['response_body']['response_payload']['update_response'];print('Signed fictional financial address update',[(x['status'],x.get('status_reason_code')) for x in updates])
assert len(updates)==1 and updates[0]['status'] in ('SUCCESS','succ')
pb=r.Odoo('pbms-odoo','pbmsdb');wid=pb.call('g2p.warehouse','search',[[['warehouse_mnemonic','=','EXAMPLE-BANK']]])[0]
pb.upsert('g2p.warehouse.program.benefit.codes',[['program_id','=',job['program_id']],['benefit_code_id','=',job['benefit_code_id']]],{'warehouse_id':wid,'program_id':job['program_id'],'benefit_code_id':job['benefit_code_id'],'additional_info':'#ACCOUNT#PHASE1-DEMO-TREASURY#TYPE#BANK_ACCOUNT#BRANCH#LAB'})
listing=pb.call('g2p.beneficiary.list','read',[[job['listing_id']]],{'fields':['list_workflow_status','envelope_creation_status']})[0]
assert listing['list_workflow_status']!='approved_for_disbursement','Already approved; never regenerate duplicate payment envelopes.'
pb.call('g2p.beneficiary.list','write',[[job['listing_id']],{'list_workflow_status':'approved_for_disbursement','approval_date':str(dt.date.today()),'envelope_creation_status':'pending','envelope_creation_number_of_attempts':0}])
pb.call('g2p.disbursement.cycle','write',[[job['cycle_id']],{'approved_for_disbursement':True}])
print('One fictional household approved for native local-bank processing; no real funds or external rail.')
