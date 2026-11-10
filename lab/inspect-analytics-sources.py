from labdb import query
for db,service in [('pbmsdb','pbms-postgresql'),('register','commons-postgresql'),('awe','commons-postgresql'),('bridge_db','commons-postgresql')]:
 print(db,query(db,"SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name IN ('g2p_program_definition','g2p_beneficiary_list','g2p_entitlement','g2p_enrollment_cycle','g2p_register_change_requests','approval_request','disbursements','disbursement_recons','disbursement_batch_control') ORDER BY table_name,ordinal_position",host_service=service,secret_name=service))
