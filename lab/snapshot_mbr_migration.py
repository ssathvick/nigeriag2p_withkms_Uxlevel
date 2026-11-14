"""Private full backups plus disposable restore databases for migration rehearsal."""
import datetime,json,os,subprocess
from pathlib import Path
from psycopg2 import sql
from test_mbr_db_connection import connect

stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
directory=Path('/opt/openg2p-lab/registration/migration-backups')/stamp
directory.mkdir(parents=True,mode=0o700)
manifest={'directory':str(directory),'databases':{}}
connection=connect();dsn=connection.info.dsn_parameters
# libpq's DSN deliberately omits the password; read it through the same private cluster secret mechanism.
import base64
secret=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret','commons-postgresql','-o','json'],text=True))
environment={**os.environ,'PGPASSWORD':base64.b64decode(secret['data']['postgres-password']).decode()}
connection.autocommit=True
try:
 for database in ['register','awe']:
  target='mbr_rehearsal_'+stamp+'_'+database;backup=directory/(database+'.dump')
  with backup.open('wb') as stream:
   result=subprocess.run(['kubectl','-n','nigeria','exec','commons-postgresql-0','--','bash','-c','export PGPASSWORD="$POSTGRES_POSTGRES_PASSWORD"; exec pg_dump -U postgres -d "$1" -Fc','mbr-backup',database],stdout=stream,stderr=subprocess.PIPE)
  if result.returncode:raise RuntimeError(result.stderr.decode())
  backup.chmod(0o600)
  with connection.cursor() as cur:cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(target)))
  with backup.open('rb') as stream:
   result=subprocess.run(['kubectl','-n','nigeria','exec','-i','commons-postgresql-0','--','bash','-c','export PGPASSWORD="$POSTGRES_POSTGRES_PASSWORD"; exec pg_restore -U postgres -d "$1" --no-owner --no-acl','mbr-restore',target],stdin=stream,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if result.returncode:raise RuntimeError(result.stderr.decode())
  manifest['databases'][database]={'rehearsal':target,'backup':str(backup)}
 p=directory/'manifest.json';p.write_text(json.dumps(manifest,indent=2));p.chmod(0o600)
 print(json.dumps(manifest))
finally:connection.close()
