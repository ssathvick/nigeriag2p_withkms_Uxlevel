import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
out={}
with r.pg('iam') as c:
 with c.cursor() as q:
  q.execute("SELECT table_name,column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name LIKE 'staff%' ORDER BY table_name,ordinal_position");out['schema']=q.fetchall()
  q.execute('SELECT r.role_mnemonic,p.permission_mnemonic FROM staff_roles r JOIN staff_role_permissions rp ON rp.role_id=r.id JOIN staff_application_permissions p ON p.id=rp.permission_id WHERE r.application_id=7 AND r.active AND rp.active AND p.active ORDER BY 1,2');out['permissions']=q.fetchall()
  q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%user%'");out['user_tables']=q.fetchall()
p=Path(__file__).parent/'role-audit.json';p.write_text(json.dumps(out,default=str,indent=2));print(json.dumps(out['permissions']));print(out['user_tables'])
