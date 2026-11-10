"""Run isolated automated suites and retain actual results, never formal sign-off."""
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
root=Path(__file__).parent
output=root/'phase1-evidence';output.mkdir(exist_ok=True)
stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
results=[]
for name in ['test-persona-workspaces.py','test-knowledge.py','test-geography.py','test-analytics.py','test-simulation.py','test-phase1-sandbox.py','test-phase1-readiness.py']:
    run=subprocess.run([sys.executable,str(root/name)],capture_output=True,text=True,timeout=120,cwd=root)
    log=run.stdout+run.stderr
    (output/(stamp+'-'+name+'.txt')).write_text(log,encoding='utf-8')
    count=re.search(r'Ran (\d+) tests?',log)
    results.append({'suite':name,'status':'passed' if run.returncode==0 else 'failed','tests':int(count.group(1)) if count else None,'evidence_file':stamp+'-'+name+'.txt'})
report={'tested_at_utc':stamp,'scope':'Isolated automated sandbox tests; not NSIPA UAT acceptance','suites':results,'formal_uat_status':'Not run','pending':['1M native payment batch and full six-programme concurrent workflow load tests','Registry API and deduplication capacity beyond the separate 38M core SQL benchmark','Native partner-management capacity beyond the separate 50,000 demo-agent benchmark','48-hour real-device offline test and GPS/biometric validation','Full portal language review and WCAG 2.1 AA audit','Availability measurement and security/penetration review','Authorised client UAT execution and sign-off','Six-LGA actual CCT pilot and independent evaluation']}
path=output/(stamp+'-results.json');path.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
sys.exit(0 if all(x['status']=='passed' for x in results) else 1)
