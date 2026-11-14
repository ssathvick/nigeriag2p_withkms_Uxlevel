from pathlib import Path
import subprocess,json,sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from test_mbr_db_connection import connect
root=Path(__file__).parent
for path in ['awe/main.py','awe/services/auth.py','awe/controllers/task.py','awe/controllers/request.py']:
 out=root/'original'/path;out.parent.mkdir(parents=True,exist_ok=True)
 out.write_bytes(subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/commons-services-awe','--','cat','/usr/local/lib/python3.13/site-packages/'+path]))
with connect('awe') as c:
 with c.cursor() as q:
  q.execute("SELECT table_name,json_agg(column_name ORDER BY ordinal_position) FROM information_schema.columns WHERE table_schema='public' GROUP BY table_name ORDER BY table_name")
  schema=dict(q.fetchall());(root/'awe-schema.json').write_text(json.dumps(schema,indent=2));print('AWE tables',list(schema))
