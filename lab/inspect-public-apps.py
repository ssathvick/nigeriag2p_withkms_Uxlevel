exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/update-public-database-urls.py').read().split('targets=')[0])
print(sql('commons-postgresql','iam',"select column_name from information_schema.columns where table_name='staff_portal_applications';"))
print(sql('commons-postgresql','iam',"select application_url from staff_portal_applications;"))
