import json,subprocess
from pathlib import Path
root=Path(__file__).parent
old='definition.register_mnemonic == "household"';new='str(definition.register_mnemonic).lower() == "household"'
for p in [root/'patch_native.py',root/'patched/register-staff-portal-api/intake_form_data_service.py']:
 p.write_text(p.read_text(encoding='utf-8-sig').replace(old,new))
cm=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','cm','nsipa-client-review-registry','-o','json'],text=True))
cm['data']={k:v.replace(old,new) for k,v in cm['data'].items()}
subprocess.run(['kubectl','replace','-f','-'],input=json.dumps(cm),text=True,check=True)
subprocess.run(['kubectl','-n','nigeria','rollout','restart','deploy/register-staff-portal-api'],check=True)
