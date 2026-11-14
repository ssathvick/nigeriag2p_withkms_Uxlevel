import json,re,difflib
from pathlib import Path
from test_mbr_db_connection import connect
from psycopg2.extras import RealDictCursor
p=Path(__file__).parent;data=json.loads((p/'field-app/android/assets/locations.json').read_text());norm=lambda s:re.sub('[^a-z0-9]','',s.lower()).replace('federalcapitalterritory','fct').replace('abujafct','fct')
with connect('master_data') as c:
 with c.cursor(cursor_factory=RealDictCursor) as q:q.execute('select * from g2p_geo_level_values');rows=q.fetchall()
states={norm(r['level_value_mnemonic']):r for r in rows if r['level_id']=='state'};mapping={};miss=[]
for s in data['states']:
 n=norm(s['name']);r=states.get(n)
 if not r:miss.append(('state',s['name'],list(states)));continue
 mapping[s['id']]=r['level_value_id']
for l in data['lgas']:
 parent=mapping.get(l['parent']);candidates=[r for r in rows if r['level_id']=='lga' and r['parent_level_value_id']==parent];matches=[r for r in candidates if norm(r['level_value_mnemonic'])==norm(l['name'])]
 if len(matches)==1:mapping[l['id']]=matches[0]['level_value_id']
 else:miss.append(('lga',l['name'],[r['level_value_mnemonic'] for r in candidates]))
(p/'household-parity/mobile-geo-crosswalk.json').write_text(json.dumps(mapping,indent=2));print(json.dumps({'mapped':len(mapping),'missing':miss},default=str))
