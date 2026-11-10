"""Use a private schema clone, strict disk budgets and authentic registry indexes."""
import argparse,datetime as dt,json,re,subprocess,sys,time,uuid
from pathlib import Path
from psycopg2 import sql
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
p=argparse.ArgumentParser();p.add_argument('--target',type=int,default=1000000);p.add_argument('--budget-gib',type=int,default=24);args=p.parse_args()
assert 1<=args.target<=38000000 and 1<=args.budget_gib<=40
schema='phase1_capacity_'+uuid.uuid4().hex[:12]
report={'scope':'Native PostgreSQL registry table and index clone in an isolated private schema','required_target':38000000,'requested_records':args.target,'resource_budget_gib':args.budget_gib,'schema':schema,'started_at_utc':r.stamp(),'samples':[],'limitations':['SQL storage/index workload, not an application API or biometric de-duplication certificate']}
output=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/capacity-native-registry.json')
c=r.pg('register');c.autocommit=True
with c.cursor() as cur:
 cur.execute("SET statement_timeout='120s'")
 cur.execute("SELECT row_to_json(t) FROM public.g2p_register_individuals t WHERE functional_record_id LIKE 'NG-LAB-%' LIMIT 1")
 seed=cur.fetchone()
 if not seed:raise RuntimeError('A known synthetic registry fixture is required.')
 seed=json.dumps(seed[0]);table=sql.Identifier(schema,'individuals')
 try:
  cur.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))
  cur.execute(sql.SQL('CREATE TABLE {} (LIKE public.g2p_register_individuals INCLUDING ALL)').format(table))
  loaded=0
  while loaded<args.target:
   end=min(loaded+100000,args.target);start=time.perf_counter()
   query=sql.SQL("INSERT INTO {} SELECT record.* FROM generate_series(%s,%s) i CROSS JOIN LATERAL jsonb_populate_record(NULL::{},%s::jsonb || jsonb_build_object('internal_record_id',md5('phase1-capacity-'||i::text),'functional_record_id','PHASE1-LOAD-I-'||i::text,'record_name','Fictional capacity record '||i::text,'full_name','Fictional capacity record '||i::text,'search_text','Fictional capacity record '||i::text)) AS record").format(table,table)
   cur.execute(query,(loaded+1,end,seed));loaded=end
   cur.execute('SELECT pg_total_relation_size(%s)',(schema+'.individuals',));size=cur.fetchone()[0]
   report['samples'].append({'records':loaded,'chunk_seconds':round(time.perf_counter()-start,3),'total_bytes':size})
   print('Private native registry capacity sample',loaded,'records;',round(size/(1024**3),3),'GiB',flush=True)
   projected=size/loaded*args.target
   if projected>args.budget_gib*1024**3:
    report['status']='resource_budget_exceeded';report['projected_bytes']=int(projected);break
  cur.execute(sql.SQL('ANALYZE {}').format(table));timings=[]
  for i in (1,max(1,loaded//2),loaded)*10:
   start=time.perf_counter();cur.execute(sql.SQL('SELECT record_name FROM {} WHERE internal_record_id=%s').format(table),( __import__('hashlib').md5(('phase1-capacity-'+str(i)).encode()).hexdigest(),));assert cur.fetchone();timings.append(time.perf_counter()-start)
  cur.execute(sql.SQL('SELECT COUNT(*) FROM {}').format(table));report['verified_records']=cur.fetchone()[0]
  report['lookup_p95_seconds']=round(sorted(timings)[int(.95*(len(timings)-1))],5)
  report.setdefault('status','passed_requested_workload')
  report['full_38m_target_status']='passed_core_sql_only' if report['verified_records']>=38000000 else 'Not run at full target'
 finally:
  # Only the unique schema created above can be removed; live public tables are untouched.
  assert re.fullmatch(r'phase1_capacity_[a-f0-9]{12}',schema)
  cur.execute(sql.SQL('DROP SCHEMA IF EXISTS {} CASCADE').format(sql.Identifier(schema)))
  report['private_schema_removed']=True;report['finished_at_utc']=r.stamp();output.write_text(json.dumps(report,indent=2))
c.close();print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2))
