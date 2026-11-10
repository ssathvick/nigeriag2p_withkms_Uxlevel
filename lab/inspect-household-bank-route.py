import sys,json,requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
data=requests.get(r.svc('spar-openg2p-spar-mapper-api')+'/openapi.json',timeout=10).json();print('Mapper contracts',list(data['paths']))
for name,schema in data.get('components',{}).get('schemas',{}).items():
 if 'Update' in name:print(name,json.dumps(schema))
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute("SELECT bank_code,bank_account_number,COUNT(*) FROM disbursement_resolution_financial_address WHERE beneficiary_id LIKE 'IQS-REG-HH-%' GROUP BY bank_code,bank_account_number");print('Native resolved fictional routes',cur.fetchall())
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT beneficiary_bank_code,beneficiary_account,payment_amount FROM initiate_payment_requests WHERE beneficiary_account='LAB-HH-000001'");print('Native bank instructions',cur.fetchall())
