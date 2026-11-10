"""Retest the existing synthetic integration account without exposing runtime logs."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
root=Path(__file__).parent;out=root/'phase1-evidence'
private=Path('/opt/openg2p-lab/registration/phase1-private-tests');private.mkdir(exist_ok=True,mode=0o700)
result={'started_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Existing synthetic account and native registry/PBMS integration'}
try:
    run=subprocess.run([sys.executable,str(root/'test-registration-integration.py')],capture_output=True,text=True,timeout=360)
    log=private/'registration-integration.log';log.write_text(run.stdout+run.stderr);log.chmod(0o600)
    result['status']='passed' if run.returncode==0 else 'failed'
    path=Path('/opt/openg2p-lab/registration/test-results.json')
    if run.returncode==0 and path.is_file():
        data=json.loads(path.read_text());result['checks']={k:v for k,v in data.items() if v=='passed'}
    else:result['next_action']='Inspect restricted diagnostic log; no failed test is counted as passed.'
except subprocess.TimeoutExpired:
    result['status']='blocked';result['next_action']='Native processing exceeded the 360-second test deadline.'
result['finished_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
(out/'native-registration-uat.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
