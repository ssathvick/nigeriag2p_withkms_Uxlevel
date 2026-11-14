import json
from pathlib import Path
d=json.loads(Path('territory-data/public/data.json').read_text())
print([(r['name'],r['constituency'],[x['name'] for x in d['districts'] if x['state_id']==r['state_id']]) for r in d['representatives']['members'] if r['chamber']=='Senate' and not r['district_id']])
print([(r['name'],r['constituency']) for r in d['representatives']['members'] if 'Conflicting' in r['status']])
print(sorted([(len(r['bills']),r['name']) for r in d['representatives']['members']],reverse=True)[:10])
