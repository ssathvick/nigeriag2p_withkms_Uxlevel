import json,re
from pathlib import Path
root=Path(__file__).parent/'registry-ui-source';messages=json.loads((root/'locales/en.json').read_text(encoding='utf-8-sig'));keys=set()
for path in (root/'src').rglob('*.tsx'):
 text=path.read_text(encoding='utf-8-sig')
 keys.update(re.findall(r'\bt\([\x27\x22]([a-zA-Z0-9_.-]+)[\x27\x22]',text))
missing=[]
for key in sorted(keys):
 value=messages
 for part in key.split('.'):
  if not isinstance(value,dict) or part not in value:missing.append(key);break
  value=value[part]
out=root.parent.parent/'output/application-consistency-verification/static-label-audit.json';out.write_text(json.dumps({'status':'passed' if not missing else 'failed','explicit_translation_keys_checked':len(keys),'missing':missing,'locale':'en'},indent=2))
assert not missing,missing
print('PASS '+str(len(keys))+' explicit English translation keys; none missing')
