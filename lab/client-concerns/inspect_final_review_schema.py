import sys
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
with r.pg('awe') as db:
 with db.cursor() as q:
  q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND (table_name LIKE '%task%' OR table_name LIKE '%decision%' OR table_name LIKE '%request%')")
  names=[x[0] for x in q.fetchall()]
  for table in names:
   q.execute('SELECT column_name FROM information_schema.columns WHERE table_name=%s',(table,));print(table,[x[0] for x in q.fetchall()])
