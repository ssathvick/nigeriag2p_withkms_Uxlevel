from pathlib import Path
import re
s=Path('territory-data/raw/naltf-senators.html').read_text()
for term in ['pagination','foogallery','lazy','ajax']:
 print(term,[s[max(0,m.start()-90):m.start()+300] for m in list(re.finditer(term,s,re.I))[-5:]])
s=Path('territory-data/raw/naltf-bills.js').read_text();i=s.index('og="https://billtracker');print(s[i:i+12000])
