import sys
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
print(query('postgres','SELECT datname,count(*) FROM pg_stat_activity GROUP BY datname;'))
print(query('postgres','SELECT rolname FROM pg_roles WHERE rolcanlogin;'))
