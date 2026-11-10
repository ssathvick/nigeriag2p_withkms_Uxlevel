import json,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;out={}
with r.pg('register') as c:
 with c.cursor() as q:
  for name in ['dedup_results_intake_forms_vs_register','dedup_results_intake_forms_vs_intake_forms']:
   q.execute('SELECT row_to_json(t) FROM '+name+' t LIMIT 3');out[name]=[x[0] for x in q.fetchall()]
(root/'duplicate-evidence.json').write_text(json.dumps(out,indent=2,default=str));print(json.dumps(out,default=str)[:5000])
