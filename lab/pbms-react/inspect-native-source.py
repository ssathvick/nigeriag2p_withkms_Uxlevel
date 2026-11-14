import subprocess,pathlib,json
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/backend-reference');root.mkdir(exist_ok=True)
def run(args):return subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/pbms-odoo','--']+args,text=True)
files=run(['find','/opt/odoo/extraaddons/openg2p-pbms','-type','f']).splitlines()
for p in files:
 if p.endswith('.py') and any(x in p for x in ['program_definition','beneficiary_list/','enrollment_cycle','disbursement_cycle','program_access','program_benefit','entitlement_rule','eligibility_rule']):
  name=p.split('/openg2p-pbms/')[1].replace('/','__');(root/name).write_text(run(['cat',p]))
print('\n'.join(p.name for p in root.iterdir()))
print(run(['sh','-c','find / -name odoo.conf 2>/dev/null; ps -ef | grep odoo | head -5']))
