import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute("SELECT section_id,section_ui_schema FROM g2p_register_sections WHERE register_id='a0000000-0000-4000-8000-000000000002'")
  for id,s in q.fetchall():
   if 'gps' in json.dumps(s).lower():print(id,json.dumps(s))
