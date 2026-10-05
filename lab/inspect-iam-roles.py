exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-iam-db.py').read().split("for db in")[0])
for table in ['staff_roles','staff_role_permissions','staff_application_permissions','staff_portal_applications']:
 print(table,query('iam',f"SELECT column_name,data_type,is_nullable FROM information_schema.columns WHERE table_name='{table}';"))
 print(query('iam',f'SELECT row_to_json(t) FROM {table} t LIMIT 8;')[:6500])
