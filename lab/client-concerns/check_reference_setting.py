import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
with r.pg('register') as db:
 with db.cursor() as q:
  q.execute("SELECT application_reference FROM g2p_intake_form_submissions WHERE submission_id='b8c8fa1f-5ae7-4138-ab05-db499676a0e4'");print(q.fetchone())
import subprocess
code="from pathlib import Path;[(print(p),print(p.read_text()[:3500])) for p in Path('/usr/local/lib/python3.12/site-packages').glob('openg2p_registry_staff*/config.py')]"
print(subprocess.run(['kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','python','-c',code],capture_output=True,text=True).stdout)
