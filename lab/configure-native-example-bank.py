"""Configure only the installed synthetic bank; retain private config backups."""
import datetime as dt,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
bank_service='openg2p-g2p-bridge-example-bank-api'
backup=r.ROOT/'phase1-bank-backups'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ');backup.mkdir(parents=True,mode=0o700)
raw=subprocess.check_output(['kubectl','-n','nigeria','get','deploy','bridge-celery-worker','-o','json'],text=True)
(backup/'worker-deployment.json').write_text(raw);(backup/'worker-deployment.json').chmod(0o600)
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute('SELECT DISTINCT beneficiary_id,bank_account_number FROM disbursement_resolution_financial_address');resolved=cur.fetchall()
  if not resolved or any(not ref.startswith('NG-LAB-') or not account or not account.startswith('LAB-') for ref,account in resolved):raise RuntimeError('Expected strictly synthetic mapped beneficiaries before bank setup.')
  cur.execute("SELECT DISTINCT benefit_program_id,benefit_code_id FROM disbursement_envelopes WHERE benefit_program_mnemonic='NG_LAB_FARMER'");programmes=cur.fetchall()
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute('SELECT account_number,book_balance,available_balance,blocked_amount FROM accounts')
  (backup/'accounts-before.json').write_text(json.dumps(cur.fetchall(),default=str))
  for index,(account,amount) in enumerate([('PHASE1-DEMO-TREASURY',10000000)]+[(account,0) for ref,account in resolved]):
   phone='0000000000' if account=='PHASE1-DEMO-TREASURY' else account.rsplit('-',1)[-1].zfill(10)
   cur.execute('''INSERT INTO accounts(account_holder_name,account_number,account_currency,account_holder_phone,account_holder_email,book_balance,available_balance,blocked_amount,created_at,updated_at,active)
   SELECT %s,%s,'NGN',%s,%s,%s,%s,0,now(),now(),true WHERE NOT EXISTS(SELECT 1 FROM accounts WHERE account_number=%s AND account_currency='NGN')''',('Phase 1 fictional account',account,phone,'phase1-bank-'+account.lower()+'@example.invalid',amount,amount,account))
pb=r.Odoo('pbms-odoo','pbmsdb')
model='g2p.warehouse.program.benefit.codes'
existing=pb.call(model,'search_read',[[]],{'fields':['id','program_id','benefit_code_id','additional_info','warehouse_id']})
(backup/'warehouse-before.json').write_text(json.dumps(existing));(backup/'warehouse-before.json').chmod(0o600)
wid=pb.upsert('g2p.warehouse',[['warehouse_mnemonic','=','EXAMPLE-BANK']],{'name':'Phase 1 Local Example Bank Simulator','warehouse_mnemonic':'EXAMPLE-BANK','is_sponsor_bank':True})
for pid,bid in programmes:
 pb.upsert(model,[['program_id','=',pid],['benefit_code_id','=',bid]],{'warehouse_id':wid,'program_id':pid,'benefit_code_id':bid,'additional_info':'#ACCOUNT#PHASE1-DEMO-TREASURY#TYPE#BANK_ACCOUNT#BRANCH#LAB'})
env={
'G2P_BRIDGE_BANK_CONNECTORS_FUNDS_AVAILABLE_CHECK_URL_EXAMPLE_BANK':'http://'+bank_service+'/check_funds',
'G2P_BRIDGE_BANK_CONNECTORS_FUNDS_BLOCK_URL_EXAMPLE_BANK':'http://'+bank_service+'/block_funds',
'G2P_BRIDGE_BANK_CONNECTORS_FUNDS_DISBURSEMENT_URL_EXAMPLE_BANK':'http://'+bank_service+'/initiate_payment'}
subprocess.run(['kubectl','-n','nigeria','set','env','deploy/bridge-celery-worker',*[k+'='+v for k,v in env.items()]],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/bridge-celery-worker','--timeout=90s'],check=True)
print('Configured local synthetic bank and sponsor account. No production rails. Private backup:',backup)
