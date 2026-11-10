import sys,json,subprocess
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
for deployment in ['bridge-celery-worker','openg2p-g2p-bridge-example-bank-celery']:
 d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',deployment,'-o','json']))
 print(deployment,{x['name']:x.get('value','REFERENCE') for x in d['spec']['template']['spec']['containers'][0].get('env',[]) if ('URL' in x['name'] and any(t in x['name'] for t in ['BANK','CALLBACK','MAPPER']))})
for db,service,tables in [('awe','commons-postgresql',['approval_request','approval_task']),('bridge_db','commons-postgresql',['disbursements','disbursement_recons','disbursement_envelopes','disbursement_resolution_financial_address']),('example_bank_db','example-bank-postgresql',['accounts','account_logs','initiate_payment_requests','initiate_payment_batch_requests','account_statement_requests'])]:
 with r.pg(db,service) as c:
  with c.cursor() as cur:
   for table in tables:
    cur.execute('SELECT column_name,data_type FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position',(table,));print(db,table,cur.fetchall())
pb=r.Odoo('pbms-odoo','pbmsdb')
print('WAREHOUSE',pb.call('g2p.warehouse','search_read',[[['warehouse_mnemonic','=','EXAMPLE-BANK']]],{'fields':['id','name','warehouse_mnemonic']}))
print('LIST_FIELDS', {k:v for k,v in pb.call('g2p.beneficiary.list','fields_get',[],{'attributes':['type','selection']}).items() if any(x in k for x in ['status','envelope','beneficiary_list_id','count','number_of'])})
print('GEOGRAPHY',[a for a in r.nigeria_geography.CATALOGUE['areas'] if a['name'] in ['Plateau','Jos North','Jos South','Jos East','Bassa']])
