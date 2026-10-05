import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
print(query('postgres',"SELECT datname FROM pg_database WHERE datistemplate=false;"))
for db in ['iam','iamdb','staff_iam']:
 try:
  print(db,query(db,"SELECT table_name FROM information_schema.tables WHERE table_schema='public';"))
 except Exception:pass
