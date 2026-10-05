import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
print('Approval tasks',query('awe',"SELECT id,assignee,status FROM approval_task WHERE request_id='700ca35f-d97d-4f6d-84e5-3be9d3a75049';"))
print('Approval decisions',query('awe',"SELECT action,actor FROM approval_decision WHERE request_id='700ca35f-d97d-4f6d-84e5-3be9d3a75049';"))
print('BG envelopes',query('bgtaskdb','SELECT row_to_json(t) FROM disbursement_envelope t;',host_service='pbms-postgresql',secret_name='pbms-postgresql'))
print('BG batches',query('bgtaskdb','SELECT row_to_json(t) FROM disbursement_batch t;',host_service='pbms-postgresql',secret_name='pbms-postgresql')[:2000])
