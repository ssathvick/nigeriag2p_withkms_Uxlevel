import json,subprocess
from pathlib import Path
root=Path(__file__).parent
cm=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','cm','nsipa-client-review-registry','-o','json'],text=True))
for key,s in cm['data'].items():
 if 'async def save_intake_form_submission_with_session(' not in s:continue
 marker='''        records_for_validation = self._records_for_validation(records)
        # Same coded-value'''
 replacement='''        records_for_validation = self._records_for_validation(records)
        if section_id == "hh_composition_headship":
            for row in records_for_validation:
                if not str(row.get("record_name") or "").strip():
                    self._invalid_request("Household name is required. Enter a name rather than a reference number.")
        # Same coded-value'''
 assert marker in s;cm['data'][key]=s.replace(marker,replacement);(root/'patched/register-staff-portal-api/intake_form_data_service.py').write_text(cm['data'][key])
subprocess.run(['kubectl','replace','-f','-'],input=json.dumps(cm),text=True,check=True)
subprocess.run(['kubectl','-n','nigeria','rollout','restart','deploy/register-staff-portal-api'],check=True,stderr=subprocess.DEVNULL)
