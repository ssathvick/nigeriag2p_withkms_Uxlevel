import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
print(query('awe',"SELECT r.artifact_id,r.id,r.status,t.id,t.assignee,t.status FROM approval_request r LEFT JOIN approval_task t ON t.request_id=r.id WHERE r.artifact_id LIKE 'IQS-SYN%' ORDER BY r.artifact_id;"))
