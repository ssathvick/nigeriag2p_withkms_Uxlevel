import sys,re
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
schema='phase1_capacity_2fdaf601a5e6'
with r.pg('register') as c:
 with c.cursor() as cur:
  cur.execute("SELECT pid,query FROM pg_stat_activity WHERE datname='register' AND pid<>pg_backend_pid() AND state='active'")
  for pid,query in cur.fetchall():
   if query.startswith('INSERT INTO "'+schema+'".'):
    cur.execute('SELECT pg_cancel_backend(%s)',(pid,));print('Cancelled only own scratch-schema generator',cur.fetchone()[0])
