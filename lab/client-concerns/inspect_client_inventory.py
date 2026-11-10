import sys,json,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
out={}
with r.pg('register') as c:
 with c.cursor() as cur:
  cur.execute("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position")
  cols={}
  for t,k,ty in cur.fetchall():cols.setdefault(t,[]).append([k,ty])
  out['columns']=cols
  for table in ['g2p_registers','g2p_intake_form_definitions','g2p_register_sections','registry_languages']:
   if table in cols:
    cur.execute('SELECT row_to_json(t) FROM '+table+' t');out[table]=[v[0] for v in cur.fetchall()]
  for table in ['g2p_register_households','g2p_intake_form_submissions']:
   if table in cols:
    cur.execute('SELECT row_to_json(t) FROM '+table+' t LIMIT 5');out[table]=[v[0] for v in cur.fetchall()]
with r.pg('awe') as c:
 with c.cursor() as cur:
  cur.execute("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position")
  out['awe_columns']=cur.fetchall()
p=Path(__file__).parent/'inventory.json';p.write_text(json.dumps(out,indent=2,default=str));p.chmod(0o600)
print('Register tables:',', '.join(out['columns']));print('Saved metadata and five synthetic sample rows for local analysis.')
