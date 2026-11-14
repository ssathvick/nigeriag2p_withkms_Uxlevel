import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%intake%house%' OR table_name LIKE '%submission%')")
  names=[x[0] for x in q.fetchall()]
  for name in names:
   q.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s",(name,));print(name,[x[0] for x in q.fetchall()])
