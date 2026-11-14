import json
from pathlib import Path
import test_meeting_native_workflow as t
data=json.loads((t.OUT/'browser-draft-state.json').read_text())
for sid in data['submission_ids']:
 d=t.detail({'id':sid});print(sid,d['draft_status'],[(s['section_id'],len(s['records'])) for s in d['section_payloads']])
 if sid==data['submission_ids'][-1]:
  row=d['section_payloads'][0]['records'][0];row['edit_action']='UPDATE'
  saved,_=t.call('aarin@gmail.com','intake-form/save-intake-form-submission',{'submission_id':sid,'form_id':t.FORM,'register_id':t.REG,'section_id':'hh_composition_headship','section_register_id':t.REG,'section_payload':[row]})
  print('Save shape',type(saved.get('section_payloads')).__name__)
