import json,re,collections
from pathlib import Path
p=Path('territory-data/raw');rs=json.loads((p/'representative-roster-extracted.json').read_text())
for r in rs:
 if r['chamber']=='Senate':print(r['name'],r['raw'])
b=json.loads((p/'naltf-bills.json').read_text());print('firstdates',min(str(x.get('firstReading')) for x in b if x.get('firstReading')),max(str(x.get('firstReading')) for x in b if x.get('firstReading')));print('numduplicate',sum(n-1 for n in collections.Counter(x['number'] for x in b).values() if n>1));print('chambers',collections.Counter((x.get('sponsor') or {}).get('chamber') for x in b))
