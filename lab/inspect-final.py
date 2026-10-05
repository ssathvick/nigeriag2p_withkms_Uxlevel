import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
for table in ['g2p_register_individuals','g2p_register_households','g2p_register_definitions','g2p_register_sections','g2p_registry_awe_policy_configurations']:
 print(table,query('register',f"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position;"))
 print('ROWS',query('register',f'SELECT row_to_json(t) FROM {table} t LIMIT 1;')[:3000])
print('callbacks',query('awe','SELECT column_name,data_type,is_nullable FROM information_schema.columns WHERE table_name=\'callback_secret\';'))
print('master DOB',query('master_data',"SELECT column_name,data_type FROM information_schema.columns WHERE table_name='g2p_sample_individuals';"))
