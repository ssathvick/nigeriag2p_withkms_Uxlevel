"""Provision aggregate-only read views and isolated, idempotent demo records."""
from pathlib import Path
import base64,datetime,json,subprocess,shutil,sqlite3
import psycopg2
from psycopg2 import sql
from service_reporting import SPECS,view_name
root=Path('/opt/openg2p-lab/registration')
backup=root/'dashboard-backups'/('connections-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,mode=0o700)
target=root/'analytics-connections.json';shutil.copy2(target,backup/target.name)
with sqlite3.connect(root/'intake.sqlite') as c,sqlite3.connect(backup/'intake.sqlite') as b:c.backup(b)
config=json.loads(target.read_text());password=config['sources']['register']['password'];admins={}
def admin(server):
 if server not in admins:
  host=subprocess.check_output(['kubectl','-n','nigeria','get','svc',server,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
  secret=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret',server,'-o','json'],text=True))
  admins[server]={'host':host,'user':'postgres','password':base64.b64decode(secret['data']['postgres-password']).decode()}
 return admins[server]
for server in sorted({s['server'] for s in SPECS.values()}):
 with psycopg2.connect(**admin(server),dbname='postgres') as conn,conn.cursor() as cur:
  cur.execute("SELECT 1 FROM pg_roles WHERE rolname='g2p_analytics_reader'")
  if not cur.fetchone():
   cur.execute('CREATE ROLE g2p_analytics_reader LOGIN PASSWORD %s',(password,))
   cur.execute("ALTER ROLE g2p_analytics_reader SET default_transaction_read_only=on")
   cur.execute("ALTER ROLE g2p_analytics_reader SET statement_timeout='15s'")
for service,spec in SPECS.items():
 db=spec['database'];connection={**admin(spec['server']),'dbname':db}
 with psycopg2.connect(**connection) as conn,conn.cursor() as cur:
  cur.execute('CREATE SCHEMA IF NOT EXISTS nsipa_reporting')
  cur.execute('REVOKE ALL ON SCHEMA nsipa_reporting FROM PUBLIC')
  cur.execute('GRANT USAGE ON SCHEMA nsipa_reporting TO g2p_analytics_reader')
  for name,(query,_,_) in spec['metrics'].items():
   view=sql.Identifier('nsipa_reporting',view_name(service,name))
   cur.execute(sql.SQL('CREATE OR REPLACE VIEW {} WITH (security_barrier=true) AS SELECT label::text,value::double precision FROM ({}) AS aggregate_rows(label,value)').format(view,sql.SQL(query)))
   cur.execute(sql.SQL('REVOKE ALL ON {} FROM PUBLIC').format(view))
   cur.execute(sql.SQL('GRANT SELECT ON {} TO g2p_analytics_reader').format(view))
  if service=='beneficiary':
   cur.execute("CREATE OR REPLACE VIEW nsipa_reporting.beneficiary_membership_scope WITH (security_barrier=true) AS SELECT partner_id,COALESCE(state,'Unknown')::text AS status FROM g2p_program_membership")
   cur.execute('REVOKE ALL ON nsipa_reporting.beneficiary_membership_scope FROM PUBLIC')
   cur.execute('GRANT SELECT ON nsipa_reporting.beneficiary_membership_scope TO g2p_analytics_reader')
 config['sources'][db]={**connection,'user':'g2p_analytics_reader','password':password}
 print('Provisioned aggregate views:',service)
target.write_text(json.dumps(config));target.chmod(0o600)
with sqlite3.connect(root/'intake.sqlite') as conn:
 conn.execute('''CREATE TABLE IF NOT EXISTS dashboard_demo_records (
 record_id TEXT PRIMARY KEY,service TEXT NOT NULL,entity TEXT NOT NULL,status TEXT NOT NULL,
 region TEXT NOT NULL,created_at TEXT NOT NULL,batch TEXT NOT NULL)''')
 fixtures={
  'consent-manager':{'consent_requests':{'Awaiting response':8,'Accepted (demo)':10,'Declined (demo)':4,'Expired (demo)':2},'consent_artefacts':{'Active (demo)':6,'Revoked (demo)':3,'Expired (demo)':3}},
  'odk':{'projects':{'Active (demo)':3,'Archived (demo)':1},'forms':{'Published (demo)':5,'Draft (demo)':3},'submissions':{'Received (demo)':12,'Approved (demo)':8,'Has issues (demo)':4}}
 }
 now=datetime.datetime.now(datetime.timezone.utc)
 for service,entities in fixtures.items():
  for entity,statuses in entities.items():
   index=0
   for status,count in statuses.items():
    for _ in range(count):
     index+=1
     conn.execute('INSERT OR IGNORE INTO dashboard_demo_records VALUES(?,?,?,?,?,?,?)',
      (f'NSIPA-DEMO-20261104-{service}-{entity}-{index:03}',service,entity,status,['Lagos','Kano','FCT'][index%3],(now-datetime.timedelta(days=index%14)).isoformat(),'NSIPA-DEMO-20261104'))
  print('Demo dataset records:',service,conn.execute('SELECT COUNT(*) FROM dashboard_demo_records WHERE service=?',(service,)).fetchone()[0])
print('Private pre-change backup:',backup)
