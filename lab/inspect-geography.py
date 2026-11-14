from labdb import query
for db in ['master_data','register']:
 print(db)
 print(query(db,"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND ((table_name IN ('g2p_geo_level_values','g2p_register_individuals','g2p_register_households')) AND (column_name ~ 'geo|lat|lon|state|address|country|record_status|internal_record_id' OR table_name='g2p_geo_level_values')) ORDER BY table_name,ordinal_position;"))
print(query('register',"SELECT 'individuals',count(*),count(geo_lowest_level_value_id),count(DISTINCT geo_lowest_level_value_id) FROM g2p_register_individuals UNION ALL SELECT 'households',count(*),count(geo_lowest_level_value_id),count(DISTINCT geo_lowest_level_value_id) FROM g2p_register_households;"))
print(query('master_data',"SELECT level_id,count(*) FROM g2p_geo_level_values GROUP BY level_id;"))
