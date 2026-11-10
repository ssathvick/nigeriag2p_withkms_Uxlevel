"""Read-only installed contracts and aggregate state, without credential output."""
import json
import subprocess
import sys
from pathlib import Path
import requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
out=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence')
contracts={}
for name in ['bridge-api','openg2p-g2p-bridge-example-bank-api']:
    resp=requests.get(r.svc(name)+'/openapi.json',timeout=15)
    if resp.ok:
        data=resp.json();contracts[name]=data
        print(name,[(p,list(v)) for p,v in data['paths'].items()])
(out/'native-contracts.json').write_text(json.dumps(contracts,indent=2))
for name in ['bridge_db','example_bank_db']:
    try:
        service='commons-postgresql' if name=='bridge_db' else 'example-bank-postgresql'
        with r.pg(name,service) as c:
            with c.cursor() as cur:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
                print('Tables',name,[x[0] for x in cur.fetchall()])
                cur.execute("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position")
                (out/(name+'-columns.json')).write_text(json.dumps(cur.fetchall(),indent=2))
    except Exception:print('Database not resolved:',name)
with r.db() as c:
    print('Intake status counts',[tuple(x) for x in c.execute('SELECT status,sync_status,COUNT(*) FROM profiles GROUP BY status,sync_status')])
    print('Application status counts',[tuple(x) for x in c.execute('SELECT status,COUNT(*) FROM applications GROUP BY status')])
print('Existing integration test account', (r.ROOT/'test-account.json').exists())
