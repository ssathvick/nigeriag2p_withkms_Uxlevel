"""Idempotent local analytics provisioning. Credentials stay in a root only file."""
import base64,json,secrets,subprocess
from pathlib import Path
import psycopg2
from psycopg2 import sql
ROOT=Path('/opt/openg2p-lab/registration')
target=ROOT/'analytics-connections.json'
previous=json.loads(target.read_text()) if target.exists() else {}
reader_password=previous.get('sources',{}).get('register',{}).get('password') or secrets.token_urlsafe(32)
writer_password=previous.get('reporting',{}).get('password') or secrets.token_urlsafe(32)
def admin(service):
    host=subprocess.check_output(['kubectl','-n','nigeria','get','svc',service,'-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    secret=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret',service,'-o','json'],text=True))
    return {'host':host,'user':'postgres','password':base64.b64decode(secret['data']['postgres-password']).decode(),'dbname':'postgres'}
services={name:admin(name) for name in ['commons-postgresql','pbms-postgresql']}
tables={'register':['g2p_register_individuals','g2p_register_households','g2p_register_change_requests'],
        'pbmsdb':['g2p_program_definition','g2p_beneficiary_list'],
        'awe':['approval_request'],'bridge_db':['disbursements','disbursement_recons','disbursement_batch_control']}
config={'sources':{}}
for service,connection in services.items():
    conn=psycopg2.connect(**connection);conn.autocommit=True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname='g2p_analytics_reader'")
        if not cur.fetchone():cur.execute('CREATE ROLE g2p_analytics_reader LOGIN')
        cur.execute('ALTER ROLE g2p_analytics_reader PASSWORD %s',(reader_password,))
        cur.execute("ALTER ROLE g2p_analytics_reader SET default_transaction_read_only=on")
        cur.execute("ALTER ROLE g2p_analytics_reader SET statement_timeout='15s'")
        if service=='commons-postgresql':
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname='g2p_analytics_writer'")
            if not cur.fetchone():cur.execute('CREATE ROLE g2p_analytics_writer LOGIN')
            cur.execute('ALTER ROLE g2p_analytics_writer PASSWORD %s',(writer_password,))
            cur.execute("SELECT 1 FROM pg_database WHERE datname='g2p_analytics'")
            if not cur.fetchone():cur.execute('CREATE DATABASE g2p_analytics OWNER g2p_analytics_writer')
    conn.close()
for db,allowed in tables.items():
    service='pbms-postgresql' if db=='pbmsdb' else 'commons-postgresql'
    connection={**services[service],'dbname':db}
    with psycopg2.connect(**connection) as conn,conn.cursor() as cur:
        cur.execute('GRANT USAGE ON SCHEMA public TO g2p_analytics_reader')
        for table in allowed:cur.execute(sql.SQL('GRANT SELECT ON {} TO g2p_analytics_reader').format(sql.Identifier(table)))
    config['sources'][db]={**connection,'user':'g2p_analytics_reader','password':reader_password}
config['reporting']={**services['commons-postgresql'],'dbname':'g2p_analytics','user':'g2p_analytics_writer','password':writer_password}
with psycopg2.connect(**config['reporting']) as conn,conn.cursor() as cur:
    cur.execute('''CREATE TABLE IF NOT EXISTS aggregate_metrics(source TEXT,metric TEXT,label TEXT,value DOUBLE PRECISION,refreshed_at TIMESTAMPTZ,stale BOOLEAN);
    CREATE TABLE IF NOT EXISTS knowledge_daily_usage(day DATE,module TEXT,article INTEGER,version INTEGER,event_name TEXT,helpful INTEGER,events INTEGER,zero_results INTEGER);
    CREATE TABLE IF NOT EXISTS knowledge_governance(module TEXT,status TEXT,articles INTEGER,live INTEGER,refreshed_at TIMESTAMPTZ);
    GRANT USAGE ON SCHEMA public TO g2p_analytics_reader;
    GRANT SELECT ON aggregate_metrics,knowledge_daily_usage,knowledge_governance TO g2p_analytics_reader;''')
config['superset']={**config['reporting'],'user':'g2p_analytics_reader','password':reader_password}
target.write_text(json.dumps(config));target.chmod(0o600)
print('Read only source identities and aggregate reporting database provisioned.')
