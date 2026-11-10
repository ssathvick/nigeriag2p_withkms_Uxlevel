import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
print(query('odkdb',"select table_name,column_name from information_schema.columns where table_name in ('submissions','submission_defs','forms') order by table_name,ordinal_position;"))
