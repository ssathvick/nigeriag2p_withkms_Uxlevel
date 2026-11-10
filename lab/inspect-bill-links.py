from pathlib import Path
import re,json,collections
s=Path('territory-data/raw/naltf-bills.js').read_text()
print([m.group(0) for m in re.finditer(r'.{0,100}(?:/bills/|billId|/bill/).{0,120}',s)][:18])
b=json.loads(Path('territory-data/raw/naltf-bills.json').read_text());print('dated eligible',sum('2023-06-13'<=str(x.get('firstReading'))[:10]<='2026-11-04' for x in b));print('past',[(x['number'],x['firstReading']) for x in b if x.get('firstReading') and x['firstReading']<'2023-06-13'][:10])
