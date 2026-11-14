import requests,re
from pathlib import Path
u='https://www.crshoa.crossriverstate.gov.ng/assets/index-4-3Iryn_.js'
s=requests.get(u,timeout=25).text;Path('territory-data/raw/cross-river-app.js').write_text(s)
for w in ['Elvert','members','api/','Members']:
 print(w,[(m.start(),s[max(0,m.start()-300):m.start()+1000]) for m in list(re.finditer(w,s))[-10:]])
