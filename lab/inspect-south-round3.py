import json
from pathlib import Path
D=json.loads(Path('territory-data/public/data.json').read_text())
for s in ['Abia','Akwa Ibom','Anambra','Bayelsa','Delta','Ebonyi','Edo','Enugu','Cross River']:
 print('\n'+s)
 for r in D['representatives']['members']:
  if r['state_name']==s and r['chamber']=='State House of Assembly': print(r['id'],r['name'],r['constituency'])
