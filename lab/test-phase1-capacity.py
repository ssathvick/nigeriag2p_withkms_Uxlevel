"""Bounded isolated workload checks; does not seed or reset the live sandbox."""
import concurrent.futures,datetime as dt,importlib.util,json,statistics,time
from pathlib import Path
spec=importlib.util.spec_from_file_location('base_tests',Path(__file__).with_name('test-persona-workspaces.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base);r=base.r
stamp=r.stamp()
start=time.perf_counter()
with r.phase1_db() as c:
 c.executemany("INSERT INTO agents VALUES(?,?,'certified',1,?)",(('CAPACITY-'+str(i),'DEMO-HH-'+str(i%6+1).zfill(2),stamp) for i in range(50000)))
insert_seconds=time.perf_counter()-start
r.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',('capacity-test',json.dumps({'csrf':'test-csrf','mode':'staff','user':{'sub':'capacity-tester','name':'Capacity tester','roles':['iqs-programme-supervisor']}}),int(time.time())+600))
client=r.app.test_client();client.set_cookie('IQS-INTAKE','capacity-test',path='/registration')
times=[]
for _ in range(30):
 start=time.perf_counter();response=client.get('/registration/api/phase1/report');times.append(time.perf_counter()-start)
 assert response.status_code==200 and response.json['agent_total']==50006 and len(response.json['agents'])==200
report={'scope':'Isolated actual Phase 1 SQLite schema and Flask report endpoint','dataset_agents':50006,'certified_agents':50000,'insertion_seconds':round(insert_seconds,3),'requests':len(times),'query_p95_seconds':round(sorted(times)[int(.95*(len(times)-1))],4),'query_max_seconds':round(max(times),4),'status':'passed' if max(times)<=3 else 'failed','limitations':['Demonstration module only; upstream Partner Management and live network capacity are not certified','Six concurrent programmes and 38M registry records require their own native workload tests']}
Path(__file__).with_name('phase1-evidence').joinpath('capacity-agents.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
