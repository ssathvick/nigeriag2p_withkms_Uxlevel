import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
for table in ['g2p_register_individuals','g2p_register_households']:
 print(query('register',f"UPDATE {table} SET record_status='ACTIVE' WHERE created_by='nigeria-lab'; SELECT count(*) FROM {table} WHERE record_status='ACTIVE';"))
