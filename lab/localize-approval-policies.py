import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
print(query('awe',"UPDATE approver_rule SET rule_value=jsonb_set(rule_value::jsonb,'{user_id}','\"admin\"'::jsonb),updated_at=now() WHERE rule_type='user' AND rule_value->>'user_id' IN ('alex.carter','nina.patel');"))
print('Both local demonstration approval stages now route to the lab administrator.')
