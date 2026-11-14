from pathlib import Path
import ast
p=Path(__file__).parent/'meeting-native/patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';s=p.read_text();anchor='            for field in ("television_count", "generator_count", "household_heads_count", "rooms_count"):'
block='''            for flag,field in (("grows_crops","crops_grown"),("major_shock_experienced","shock_types")):
                if household.get(flag) == "YES" and not household.get(field):
                    self._invalid_request("Select the crops grown or major shocks when answering Yes.")
            for asset in ("television","generator"):
                if household.get("owns_"+asset) == "YES" and not household.get(asset+"_count"):
                    self._invalid_request("Enter the count for each television or generator owned.")
'''
if 'Select the crops grown' not in s:s=s.replace(anchor,block+anchor);ast.parse(s);p.write_text(s)
print('Prepared conditional survey checks')
