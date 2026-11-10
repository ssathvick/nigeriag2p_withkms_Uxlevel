import sys,requests
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
try:print('Bank service ping',requests.get(r.svc('openg2p-g2p-bridge-example-bank-api')+'/ping',timeout=5).status_code)
except requests.RequestException:print('Bank service ping unavailable')
with r.pg('register') as c:
 with c.cursor() as cur:
  cur.execute("SELECT state,wait_event_type,wait_event,extract(epoch from now()-query_start)::int,left(query,60) FROM pg_stat_activity WHERE datname='register' AND pid<>pg_backend_pid() AND state<>'idle'")
  print('Active registry work',cur.fetchall())
