from pathlib import Path
import ast
p=Path(__file__).parent/'meeting-native/patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';s=p.read_text();anchor='        incoming_ids = await self._upsert_intake_rows(\n';block='''        # Native non-list sections edit the existing submission row; generated client
        # IDs must not replace its identity or detach children after a draft is reopened.
        if not _section.is_list and len(existing_rows) == 1 and len(records) == 1:
            if records[0].get("edit_action") != "DELETE":
                records[0]["internal_record_id"] = str(next(iter(existing_rows)))
'''
if '# Native non-list sections edit' not in s:
 if anchor not in s:raise RuntimeError('Save anchor absent')
 s=s.replace(anchor,block+anchor,1);ast.parse(s);p.write_text(s)
print('Preserved native household row identity across resumed draft saves')
