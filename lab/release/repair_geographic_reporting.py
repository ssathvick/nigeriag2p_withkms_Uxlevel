"""Plan/apply the geographic aggregate reporting repair. No fixture or workflow changes."""
import argparse,base64,datetime,json,subprocess,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--namespace',default='nigeria');p.add_argument('--database',default='register');p.add_argument('--postgres-service',default='commons-postgresql');p.add_argument('--postgres-secret',default='commons-postgresql');p.add_argument('--password-key',default='postgres-password');p.add_argument('--backup-root',type=Path,default=Path('/opt/openg2p-lab/registration/analytics-backups'));a=p.parse_args()
 root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
 from geographic_reporting import GEOGRAPHY_AGGREGATES_SQL
 from service_reporting import SPECS,view_name
 metrics=SPECS['geography']['metrics'];names=[view_name('geography',m) for m in metrics]
 print(json.dumps({'apply':a.apply,'database':a.database,'namespace':a.namespace,'views':names,'function':'nsipa_reporting.geography_record_counts()','base_table_grants_added':False,'workflow_or_data_mutation':False}))
 if not a.apply:return
 import psycopg2
 def read(*args):return subprocess.check_output(['kubectl','-n',a.namespace,*args],text=True)
 host=read('get','svc',a.postgres_service,'-o','jsonpath={.spec.clusterIP}').strip();secret=json.loads(read('get','secret',a.postgres_secret,'-o','json'))
 password=base64.b64decode(secret['data'][a.password_key]).decode()
 with psycopg2.connect(host=host,dbname=a.database,user='postgres',password=password,connect_timeout=8) as conn,conn.cursor() as cur:
  cur.execute("SELECT to_regclass('public.ng2p_geography_record_counts') IS NOT NULL, to_regrole('g2p_analytics_reader') IS NOT NULL")
  if cur.fetchone()!=(True,True):raise SystemExit('Existing geography views and reporting reader are required; no changes applied.')
  cur.execute("SELECT c.relname,c.reloptions,c.relrowsecurity,c.relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname IN ('ng2p_record_geography','g2p_register_households','g2p_register_individuals') ORDER BY c.relname");before=cur.fetchall()
  cur.execute("SELECT c.relname,pg_get_viewdef(c.oid,true),c.relacl::text FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='nsipa_reporting' AND c.relname=ANY(%s)",(names,));views=cur.fetchall()
  if len(views)!=3:raise SystemExit('All three existing geography aggregate views are required; no changes applied.')
  cur.execute("SELECT pg_get_functiondef(p.oid),p.proacl::text FROM pg_proc p WHERE p.oid=to_regprocedure('nsipa_reporting.geography_record_counts()')");prior=cur.fetchone()
  backup=a.backup_root/('geographic-refresh-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,mode=0o700)
  (backup/'reporting-schema-before.json').write_text(json.dumps({'views':views,'function':prior,'native_security':before},indent=2));(backup/'reporting-schema-before.json').chmod(0o600)
  cur.execute(GEOGRAPHY_AGGREGATES_SQL)
  for metric,(query,_,_) in metrics.items():
   name=view_name('geography',metric)
   cur.execute('CREATE OR REPLACE VIEW nsipa_reporting.'+name+' WITH (security_barrier=true) AS SELECT label::text,value::double precision FROM ('+query+') AS aggregate_rows(label,value)')
  cur.execute("SELECT c.relname,c.reloptions,c.relrowsecurity,c.relforcerowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname IN ('ng2p_record_geography','g2p_register_households','g2p_register_individuals') ORDER BY c.relname");assert cur.fetchall()==before
 print('Geographic reporting views repaired atomically. Private schema recovery point: '+str(backup))
 print('Run systemctl start iqs-analytics.service, then verify its Result and fresh geographic reporting totals.')

if __name__=='__main__':main()
