import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
p=Path(__file__).parent/'state.json';s=json.loads(p.read_text())
with r.pg('register') as db:
 with db.cursor() as q:
  for key,item in s.items():
   if not isinstance(item,dict) or 'mapping' not in item:continue
   q.execute('SELECT functional_record_id FROM g2p_register_households WHERE internal_record_id=%s',(item['mapping']['payload']['internal_record_id'],))
   item['functionalId']=q.fetchone()[0]
p.write_text(json.dumps(s,indent=2));print('Registry identifiers refreshed')
