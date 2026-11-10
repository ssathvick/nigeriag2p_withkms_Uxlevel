import json
from pathlib import Path
d=json.loads(Path('territory-data/public/data.json').read_text())
print('future stages',[(b['number'],b['second_reading']) for r in d['representatives']['members'] for b in r['bills'] if b['second_reading'] and b['second_reading']>'2026-11-04'])
