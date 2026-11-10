import subprocess
code="from pathlib import Path;[(print(p),print(p.read_text()[max(0,p.read_text().find('class G2PIntakeFormSubmission')-1200):p.read_text().find('class G2PIntakeFormSubmission')+4500])) for p in Path('/usr/local/lib/python3.12/site-packages').glob('openg2p*/**/*.py') if 'class G2PIntakeFormSubmission(' in p.read_text()]"
r=subprocess.run(['kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','python','-c',code],capture_output=True,text=True);print(r.stdout)
