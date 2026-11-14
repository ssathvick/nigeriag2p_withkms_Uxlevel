import json,re
from pathlib import Path
root=Path(__file__).parent;path=root/'registry-ui-source/locales/en.json';messages=json.loads(path.read_text(encoding='utf-8-sig'))
def visit(node):
 if isinstance(node,dict):
  for key,value in node.items():
   if key in ['widget-label','section-title','section_mnemonic','form_mnemonic'] and isinstance(value,str) and re.fullmatch('[a-z][a-z0-9_]*',value):messages.setdefault(value,value.replace('_',' ').capitalize())
   else:visit(value)
 elif isinstance(node,list):
  for v in node:visit(v)
for name in ['g2p_register_sections.json','g2p_intake_form_definitions.json']:visit(json.loads((root.parent/'output/ooru-meeting-audit/native'/name).read_text()))
messages.update(household_name='Household name',household_head_name='Household head name',household_head_reference='Household head reference (optional)',household_intake_form='Household intake form',individual_intake_form='Individual intake form')
path.write_text(json.dumps(messages,ensure_ascii=False,indent=2),encoding='utf-8');print('Completed readable native field labels.')
