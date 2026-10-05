import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
tables=query('partner_management',"SELECT table_name FROM information_schema.tables WHERE table_schema='public';").splitlines()
for table in tables:
 if any(x in table for x in ['partner','key']):
  print(table,query('partner_management',f"SELECT column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_name='{table}';"))
