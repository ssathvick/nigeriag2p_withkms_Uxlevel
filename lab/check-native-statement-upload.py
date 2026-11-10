import json,sys
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT account_statement_lob FROM account_statements WHERE account_number='PHASE1-DEMO-TREASURY' AND account_statement_lob IS NOT NULL ORDER BY id LIMIT 1");lob=cur.fetchone()[0]
response=requests.post(r.svc('bridge-api')+'/upload_mt940',files={'statement_file':('phase1-native.mt940',lob.encode(),'text/plain')},timeout=15)
data=response.json() if response.headers.get('Content-Type','').startswith('application/json') else {}
header=data.get('response_header',{})
result={'http_status':response.status_code,'response_status':header.get('response_status'),'error_code':header.get('response_error_code'),'statement_id':data.get('response_body',{}).get('response_payload',{}).get('statement_id') if data.get('response_body',{}).get('response_payload') else None}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-statement-upload.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
