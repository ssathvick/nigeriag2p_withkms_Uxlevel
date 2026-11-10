import requests
from pathlib import Path
for k in ['index-CLi-IG4o.js','team-DG5Qug9k.js','bills-motions-CRXdhEvp.js']:
 s=requests.get('https://www.crshoa.crossriverstate.gov.ng/assets/'+k,timeout=25).text;Path('territory-data/raw/cross-river-'+k).write_text(s);print(k,s[:24000])
