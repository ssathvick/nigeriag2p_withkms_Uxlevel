import sys,json,datetime,copy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r,jos_connected as j
data=j.snapshot(r);first=data['rows'][0];third=data['rows'][2]
assert first['registry_status']=='complete' and first['modern_registry_id'] and first['registry_mapping']['socialregistrydb']['household']
assert first['application_status']=='enrolled' and first['calculation']['number_of_entitlements_processed']==1
assert first['awe']['status']=='approved' and len(first['bank']['instructions'])==1 and first['bank']['credited_ngn']==25000
assert first['bank']['instructions'][0]['status']=='SUCCESS'
assert len(first['bridge'])==1 and first['bridge'][0]['mapping_status']=='PROCESSED' and first['bridge'][0]['dispatch_status']=='PROCESSED'
assert len(first['bridge'][0]['reconciliations'])==1 and not first['bridge'][0]['reconciliations'][0]['reversed']
assert third['awe']['status']=='in_review' and not third['dispatch_started'] and third['bank']['credited_ngn']==0
assert data['rows'][1]['registry_status']=='not_started'
for key in ['JOS-NATIVE-001','JOS-NATIVE-003']:j.assert_calculation(r,j.run(r,key))
before=j.bank_evidence(r,'JOS-NATIVE-001');message=j.operate(r,'JOS-NATIVE-001','dispatch','verification-repeat');assert 'already authorised' in message;assert j.bank_evidence(r,'JOS-NATIVE-001')==before
try:j.operate(r,'JOS-NATIVE-003','dispatch','verification-negative')
except j.GuardError as e:assert 'AWE approval' in str(e)
else:raise AssertionError('Unapproved dispatch was not rejected')
altered=j.approval(r,j.run(r,'JOS-NATIVE-001'));altered=copy.deepcopy(altered);altered['context']['amount_ngn']=25001
with patch.object(j,'approval',return_value=altered):
 try:j.operate(r,'JOS-NATIVE-001','dispatch','verification-tamper')
 except j.GuardError as e:assert 'exact calculation' in str(e)
 else:raise AssertionError('Mismatched approval was not rejected')
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute('SELECT book_balance,available_balance,blocked_amount FROM accounts WHERE account_number=%s',(j.TREASURY,));treasury=cur.fetchone();assert treasury==(975000,975000,0),treasury
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute('SELECT count(*) FROM disbursement_envelopes WHERE benefit_program_id=%s',(41,));assert cur.fetchone()[0]==1
  cur.execute('SELECT statement_process_status FROM account_statements WHERE statement_id=%s',(first['bridge'][0]['reconciliations'][0]['statement_id'],));assert cur.fetchone()[0]=='PROCESSED'
j.routing_guard(r);j.publish(r,data)
report={'checked_at':r.stamp(),'status':'passed','synthetic':True,'real_money':False,'cohort':3,'completed':1,'approval_pending':1,'untouched_intake':1,'native_program_id':41,'native_list_id':10,'bank_credit_ngn':25000,'treasury_balance_ngn':975000,'statement_id':first['bridge'][0]['reconciliations'][0]['statement_id'],'duplicate_dispatch_preserved_bank_records':True,'unapproved_dispatch_blocked':True,'approval_amount_mismatch_blocked':True,'one_household_per_active_calculation':True,'superseded_unsent_list':12,'corrected_scoped_list':13,'limitations':data['limitations']}
out=Path('/mnt/h/Nigeria_Mosip/codex/outputs/jos-cct');(out/'native-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
