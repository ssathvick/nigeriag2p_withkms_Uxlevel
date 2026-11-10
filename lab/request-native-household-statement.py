import json,sys,time
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
resp=requests.post(r.svc('openg2p-g2p-bridge-example-bank-api')+'/generate_account_statement',json={'program_account_number':'PHASE1-DEMO-TREASURY'},timeout=15)
result={'http_status':resp.status_code,'response':resp.json(),'scope':'Native API and queued worker for the local fictional treasury only'}
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-household-statement.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
