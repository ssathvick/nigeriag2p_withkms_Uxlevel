import subprocess
code="from pathlib import Path;[(print(p),print(p.read_text()[:22000])) for p in Path('/usr/local/lib/python3.12/site-packages/iam_core/user_auth').rglob('enums.py') if 'django' not in str(p)]"
r=subprocess.run(['kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','python','-c',code],capture_output=True,text=True);print(r.stdout)
