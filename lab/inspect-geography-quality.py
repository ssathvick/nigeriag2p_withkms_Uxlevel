from labdb import query
print(query('register',"SELECT geo_lowest_level_value_id,count(*) FROM g2p_register_individuals GROUP BY 1 ORDER BY 1;"))
print(query('register',"SELECT 'individuals',count(*) FILTER(WHERE latitude IS NOT NULL AND longitude IS NOT NULL),min(latitude),max(latitude),min(longitude),max(longitude) FROM g2p_register_individuals UNION ALL SELECT 'households',count(*) FILTER(WHERE latitude IS NOT NULL AND longitude IS NOT NULL),min(latitude),max(latitude),min(longitude),max(longitude) FROM g2p_register_households;"))
print(query('register',"SELECT geo_code_hierarchy_json,count(*) FROM g2p_register_households GROUP BY 1 LIMIT 5;"))
