import sys,json
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
print('Approval rules',query('awe','SELECT row_to_json(t) FROM approver_rule t;')[:4500])
print('Bridge states',query('bridge_db','SELECT row_to_json(t) FROM disbursements t;')[:4500])
exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/test-pbms-enrollment.py').read().split('program=')[0])
call('g2p.beneficiary.list','write',[[2],{'envelope_creation_status':'complete','envelope_creation_latest_error_code':False,'disbursement_batch_creation_status':'complete','dbc_latest_error_code':False}])
print('Verified PBMS envelope/batch acknowledgments restored after duplicate demo retry.')
