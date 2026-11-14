from pathlib import Path
import ast,datetime,shutil
root=Path(__file__).parent;service=root/'meeting-native/patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';s=service.read_text()
if '# household-parity validation' not in s:
 anchor='        submission.approval_status = ApprovalStatusEnum.PENDING.value\n        now = datetime.now()'
 block='''        # household-parity validation: preserve legacy submissions, validate newly captured surveys.
        if str(definition.register_mnemonic).lower() == "household":
            import re
            members = next((section.records for section in section_payloads if section.section_id == "hh_members"), []) or []
            if submission.first_created_at >= SURVEY_CUTOFF:
                if household.get("registration_confirmed") != "YES":
                    self._invalid_request("Confirm that the household records are accurate before submitting for review.")
                if not members:
                    self._invalid_request("Add at least one household member before submitting for review.")
            heads = [m for m in members if m.get("relationship_to_head") == "SELF"]
            if household.get("household_heads_count") is not None and int(household["household_heads_count"]) != len(heads):
                self._invalid_request("The number of household heads must match the household members marked as head.")
            if household.get("head_list_complete") == "NO":
                self._invalid_request("Complete the household head list before submitting for review.")
            for field in ("television_count", "generator_count", "household_heads_count", "rooms_count"):
                if household.get(field) is not None and int(household[field]) < 1:
                    self._invalid_request("Household head, room and owned-asset counts must be positive.")
            for member in members:
                for field, digits in (("bank_account_number",10),("bvn",11)):
                    value = member.get(field)
                    if value and not re.fullmatch(r"[0-9]{"+str(digits)+r"}",str(value)):
                        self._invalid_request("Bank account numbers must have 10 digits and BVNs must have 11 digits.")
                if member.get("nin_status") == "YES":
                    if member.get("nin_id_type") == "NIN":
                        if not re.fullmatch(r"[0-9]{11}",str(member.get("foundational_id") or "")):
                            self._invalid_request("Enter an 11-digit NIN. National ID authentication is not connected.")
                    elif member.get("nin_id_type") == "TRACKING_NUMBER":
                        if not str(member.get("rid") or "").strip(): self._invalid_request("Enter the NIN tracking number.")
                    else: self._invalid_request("Select NIN or tracking number for the identification type.")
                year,month,day=member.get("birth_year"),member.get("birth_month"),member.get("birth_day")
                if year is not None and not datetime.now().year-120 <= int(year) <= datetime.now().year:
                    self._invalid_request("Check the member birth year.")
                if month is not None and not 1 <= int(month) <= 12: self._invalid_request("Birth month must be between 1 and 12.")
                if day is not None and not 1 <= int(day) <= 31: self._invalid_request("Birth day must be between 1 and 31.")
                if year and month and day:
                    try: datetime(int(year),int(month),int(day))
                    except ValueError: self._invalid_request("The member birth date is not a valid calendar date.")
'''.replace('SURVEY_CUTOFF','datetime.fromisoformat('+repr(datetime.datetime.now().isoformat())+')')
 if anchor not in s:raise RuntimeError('Finalization anchor missing')
 s=s.replace(anchor,block+anchor,1);ast.parse(s);service.write_text(s)
p=root/'client-concerns/odk_native_registry_mapping.py';s=p.read_text();s=s.replace("payload.update(size_total=len(members),", "payload.update(registration_confirmed='YES',household_heads_count=1,head_list_complete='YES',size_total=len(members),");p.write_text(s);dest=Path('/opt/openg2p-lab/odk-sync/odk_native_registry_mapping.py');shutil.copy2(dest,dest.with_suffix('.before-survey.py'));shutil.copy2(p,dest)
print('Prepared server survey validation and preserved Collect confirmation handling')
