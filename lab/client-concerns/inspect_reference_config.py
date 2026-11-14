import subprocess,json
code="from pathlib import Path;[(print(p),print('\\n'.join(l for l in p.read_text().splitlines() if 'application_reference_format' in l or 'env_prefix' in l))) for p in Path('/usr/local/lib/python3.12/site-packages/openg2p_registry_core').rglob('config.py')]"
print(subprocess.run(['kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','python','-c',code],capture_output=True,text=True).stdout)
