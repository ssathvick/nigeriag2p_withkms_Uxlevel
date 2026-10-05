"""Restore logical database backups into disposable, isolated PostgreSQL pods.

Never points a restore command at an application database. COPY row counts in
the dump are compared with the restored tables. Verification results are private.
"""
import argparse, datetime, hashlib, json, pathlib, re, sqlite3, subprocess, tarfile

parser = argparse.ArgumentParser()
parser.add_argument('directory')
args = parser.parse_args()
root = pathlib.Path(args.directory).resolve()
namespace = 'nigeriag2p-backup-check-' + datetime.datetime.now().strftime('%H%M%S')
def run(cmd, **kwargs):
    return subprocess.run(cmd, check=True, capture_output=True, **kwargs)
def kubectl(*args, **kwargs):
    return run(['kubectl', *args], **kwargs)
report = {'checked_at': datetime.datetime.now().isoformat(), 'postgresql': {}, 'sqlite': {}, 'archives': {}}
kubectl('create', 'namespace', namespace)
try:
    for dump in sorted(root.glob('*.sql')):
        image = json.loads(kubectl('-n','nigeria','get','pod',dump.stem+'-0','-o','json').stdout)['spec']['containers'][0]['image']
        pod = {'apiVersion':'v1','kind':'Pod','metadata':{'name':dump.stem,'namespace':namespace},'spec':{
            'restartPolicy':'Never','automountServiceAccountToken':False,
            'securityContext':{'runAsUser':1001,'runAsGroup':1001,'fsGroup':1001},
            'containers':[{'name':'postgres','image':image,'command':['/opt/bitnami/scripts/postgresql/entrypoint.sh','/bin/bash','-ec'],
                'args':['mkdir -p /verify/data; /opt/bitnami/postgresql/bin/initdb -D /verify/data --auth=trust >/dev/null; exec /opt/bitnami/postgresql/bin/postgres -D /verify/data -c listen_addresses=127.0.0.1 -c unix_socket_directories=/verify'],
                'volumeMounts':[{'name':'verify','mountPath':'/verify'}],
                'readinessProbe':{'exec':{'command':['/opt/bitnami/postgresql/bin/pg_isready','-h','/verify','-U','postgres']},'initialDelaySeconds':2,'periodSeconds':2}}],
            'volumes':[{'name':'verify','emptyDir':{}}]}}
        kubectl('apply','-f','-',input=json.dumps(pod).encode())
        kubectl('-n',namespace,'wait','--for=condition=Ready','pod/'+dump.stem,'--timeout=180s')
        text = dump.read_text()
        # initdb already creates postgres. Restore every other role, then alter postgres as dumped.
        text = re.sub(r'^CREATE ROLE postgres;\n', '', text, flags=re.M)
        result = kubectl('-n',namespace,'exec','-i',dump.stem,'--','/opt/bitnami/postgresql/bin/psql','-h','/verify','-U','postgres','-v','ON_ERROR_STOP=1',input=text.encode())
        (root/(dump.stem+'-restore.log')).write_bytes(result.stdout+result.stderr)
        database = 'postgres'; expected = {}; current = None; count = 0
        for line in text.splitlines():
            if line.startswith('\\connect '):
                fields = line.split()
                database = fields[-1].strip('"')
            if current is not None:
                if line == '\\.': expected[(database,current)] = count; current = None
                else: count += 1
            elif line.startswith('COPY ') and line.endswith(' FROM stdin;'):
                current = line[5:line.index(' (')]; count = 0
        for database in sorted({key[0] for key in expected}):
            entries = [(table,count) for (db,table),count in expected.items() if db==database]
            query = '\n'.join("SELECT '"+table.replace("'","''")+"', count(*) FROM ONLY "+table+';' for table,count in entries)
            output = kubectl('-n',namespace,'exec','-i',dump.stem,'--','/opt/bitnami/postgresql/bin/psql','-h','/verify','-U','postgres','-d',database,'-At','-F','\t','-v','ON_ERROR_STOP=1',input=query.encode()).stdout.decode()
            actual = {line.rsplit('\t',1)[0]:int(line.rsplit('\t',1)[1]) for line in output.splitlines()}
            for table,count in entries:
                if actual.get(table)!=count: raise RuntimeError('Row count mismatch: '+dump.stem+' '+database+' '+table)
        report['postgresql'][dump.stem] = {'restore':'passed','tables_checked':len(expected),'rows_checked':sum(expected.values()),'databases':sorted({x[0] for x in expected})}
        print(dump.stem+': restored and verified '+str(len(expected))+' tables',flush=True)
        kubectl('-n',namespace,'delete','pod',dump.stem,'--wait=true')
    db = root/'registration-intake.sqlite'
    with sqlite3.connect(db) as conn:
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        report['sqlite'] = {'integrity_check':'ok','tables':{t:conn.execute('SELECT count(*) FROM "'+t.replace('"','""')+'"').fetchone()[0] for t in tables}}
    for archive in root.glob('*.tar.gz'):
        members = 0; size = 0
        with tarfile.open(archive,'r:gz') as tf:
            for member in tf:
                if member.isfile():
                    stream = tf.extractfile(member)
                    while chunk := stream.read(1024*1024): size += len(chunk)
                members += 1
        report['archives'][archive.name] = {'read_to_end':'passed','members':members,'uncompressed_bytes':size}
    report['status'] = 'passed'
finally:
    kubectl('delete','namespace',namespace,'--wait=true','--timeout=180s')
    (root/'verification.json').write_text(json.dumps(report,indent=2))
print('Logical backup verification passed',flush=True)
