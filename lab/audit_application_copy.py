import json,re
from pathlib import Path
root=Path(__file__).parent/'registry-ui-source';path=root/'locales/en.json';messages=json.loads(path.read_text(encoding='utf-8-sig'))
copy={'actions':'Actions','due_at':'Due date','error_occurred':'An error occurred. Please try again.','invalid_json_format':'Enter valid JSON before saving.','please_fill_required_fields':'Complete the required fields before continuing.','save_failed':'Changes could not be saved. Please try again.','section_create_failed':'The section could not be created. Please try again.','section_mnemonic_required':'Enter a section name.','section_update_failed':'The section could not be updated. Please try again.','submission':'Registration submission','theme_config_name_required':'Enter a theme name.','toast_semantic_pattern_create_failed':'The semantic pattern could not be created. Please try again.'}
messages.update(copy);path.write_text(json.dumps(messages,ensure_ascii=False,indent=2)+'\n')
display_path=root/'locales/registry-display-labels.json';display=json.loads(display_path.read_text());display.update({'ACTIVE':'Active','INACTIVE':'Inactive','ARCHIVED':'Archived','CANCELLED':'Cancelled','COMPLETED':'Completed','CLAIMED':'Claimed','OPEN':'Open','n_a':'Not recorded'})
display_path.write_text(json.dumps(display,ensure_ascii=False,indent=2)+'\n')
out=Path(__file__).parent.parent/'output/application-consistency-verification';out.mkdir(exist_ok=True)
(out/'copy-fixes.json').write_text(json.dumps({'missing_static_labels_added':copy,'display_only_status_labels':{k:display[k] for k in ['ACTIVE','INACTIVE','ARCHIVED','CANCELLED','COMPLETED','CLAIMED','OPEN']},'stored_codes_changed':False},indent=2))
print('Added 12 missing labels and readable status display names; stored codes unchanged')
