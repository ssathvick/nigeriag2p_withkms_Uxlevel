import subprocess,json,base64,os,pathlib,datetime,sqlite3,tarfile,time,traceback,hashlib
meta=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/tmp/current-private-backup.json').read_text(encoding='utf-8-sig'));stamp=meta['stamp']
root=pathlib.Path('/opt/openg2p-private-backups')/stamp;root.mkdir(parents=True,mode=0o700,exist_ok=True);os.umask(0o077)
def run(cmd,**kw):return subprocess.run(cmd,check=True,capture_output=True,**kw)
def k(*args,**kw):return run(['kubectl',*args],**kw)
def get(resource,ns=True):return json.loads(k(*(['-n','nigeria'] if ns else []),'get',resource,'-o','json').stdout)
def save(name,x):(root/name).write_text(json.dumps(x,indent=2))
state=get('deploy,sts');pods=get('pods');pvs=get('pv',False);cron=get('cronjobs');jobs=get('jobs')
assert not any(x.get('status',{}).get('active',0) for x in jobs['items']),'Active jobs must settle first'
save('workloads-original.json',state);save('pods-original.json',pods);save('pv-original.json',pvs);save('cronjobs-original.json',cron)
resources='deploy,sts,ds,svc,cm,secret,pvc,sa,role,rolebinding,networkpolicy,cronjobs,ingress,virtualservice,gateway'
save('kubernetes-private.json',get(resources))
active=run(['systemctl','list-units','--type=service','--type=timer','--state=active','--no-legend','--plain'],text=True).stdout
units=[l.split()[0] for l in active.splitlines() if l.split()[0].startswith(('iqs-','nsipa-'))]
save('host-units-original.json',units)
pg=[x for x in state['items'] if x['kind']=='StatefulSet' and 'postgresql' in x['metadata']['name']]
assert len(pg)==5
def scale(items,restore=False):
 for x in items:
  n=x['metadata']['name'];rep=x['spec'].get('replicas',1) if restore else 0
  k('-n','nigeria','scale',x['kind'].lower()+'/'+n,'--replicas='+str(rep))
apps=[x for x in state['items'] if x not in pg]
def wait_remaining(allow):
 end=time.time()+180
 while time.time()<end:
  live=[p for p in get('pods')['items'] if p['status'].get('phase') not in ['Succeeded','Failed'] and not any(p['metadata']['name'].startswith(n+'-') for n in allow)]
  if not live:return
  time.sleep(2)
 raise RuntimeError('Project workloads did not quiesce')
report={'stamp':stamp,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'postgresql':[],'redis':[],'sqlite':[]}
try:
 for c in cron['items']:k('-n','nigeria','patch','cronjob',c['metadata']['name'],'--type=merge','-p','{"spec":{"suspend":true}}')
 for unit in units:run(['systemctl','stop',unit])
 # Stop host oneshot writers that may already have started from their timers.
 for unit in ['iqs-analytics.service','iqs-phase1.service','iqs-registration-sync.service','iqs-simulation.service','nsipa-odk-sync.service']:
  subprocess.run(['systemctl','stop',unit],capture_output=True)
 scale([x for x in apps if x['kind']=='Deployment' or 'keycloak' in x['metadata']['name']])
 wait_remaining([x['metadata']['name'] for x in state['items'] if x['kind']=='StatefulSet' and 'keycloak' not in x['metadata']['name']])
 for pod in pods['items']:
  name=pod['metadata']['name']
  if 'redis' not in name or pod['status'].get('phase')!='Running':continue
  k('-n','nigeria','exec',name,'--','sh','-c','unset REDISCLI_AUTH; if [ -n "${REDIS_PASSWORD:-}" ]; then export REDISCLI_AUTH="$REDIS_PASSWORD"; fi; redis-cli --rdb /tmp/nsipa-private-backup.rdb')
  (root/('redis-'+name+'.rdb')).write_bytes(k('-n','nigeria','exec',name,'--','cat','/tmp/nsipa-private-backup.rdb').stdout)
  k('-n','nigeria','exec',name,'--','rm','-f','/tmp/nsipa-private-backup.rdb');report['redis'].append(name)
 scale([x for x in apps if x['kind']=='StatefulSet'])
 wait_remaining([x['metadata']['name'] for x in pg]);print('Project writers stopped; capturing consistent database and runtime state',flush=True)
 for obj in pg:
  service=obj['metadata']['name'];secret=get('secret/'+service);password=base64.b64decode(secret['data']['postgres-password'])
  with (root/(service+'.sql')).open('wb') as f:
   p=subprocess.run(['kubectl','-n','nigeria','exec','-i','svc/'+service,'--','sh','-c','read -r PGPASSWORD; export PGPASSWORD; exec pg_dumpall -U postgres'],input=password+b'\n',stdout=f,stderr=subprocess.PIPE)
   if p.returncode:raise RuntimeError('Database dump failed: '+service)
  report['postgresql'].append(service);print('Captured database service:',service,flush=True)
 runtime=pathlib.Path('/opt/openg2p-lab');excluded={'backups','encrypted-exports','registration-venv','__pycache__','node_modules','.git','.cache'}
 for src in runtime.rglob('*'):
  if not src.is_file() or any(v in excluded for v in src.relative_to(runtime).parts):continue
  try:
   with src.open('rb') as f:magic=f.read(16)
  except OSError:continue
  if magic!=b'SQLite format 3\x00':continue
  dest=root/'sqlite'/src.relative_to(runtime);dest.parent.mkdir(parents=True,exist_ok=True)
  with sqlite3.connect('file:'+str(src)+'?mode=ro',uri=True) as a,sqlite3.connect(dest) as b:a.backup(b);assert b.execute('pragma integrity_check').fetchone()[0]=='ok'
  report['sqlite'].append(str(src))
 def filt(info):
  parts=pathlib.PurePosixPath(info.name).parts
  if any(x in excluded for x in parts):return None
  if info.issock() if hasattr(info,'issock') else False:return None
  return info
 paths=['/opt/openg2p-lab','/etc/nginx','/etc/cloudflared','/etc/rancher','/etc/systemd/system','/etc/hosts','/etc/wsl.conf','/root/.cloudflared','/home/sathvick/.cloudflared','/root/.android/ng2p-demo.keystore','/home/sathvick/.android/ng2p-demo.keystore','/var/lib/rancher/k3s/server/token']
 volume_map=[]
 for pv in pvs['items']:
  claim=pv['spec'].get('claimRef',{})
  if claim.get('namespace')!='nigeria' or 'postgresql' in claim.get('name',''):continue
  path=pv['spec'].get('hostPath',pv['spec'].get('local',{})).get('path')
  if path:paths.append(path);volume_map.append({'claim':claim['name'],'path':path})
 for pod in pods['items']:
  for v in pod['spec'].get('volumes',[]):
   path=v.get('hostPath',{}).get('path')
   if path and not path.startswith(('/var/run','/run','/proc','/sys')) and 'postgresql' not in path:paths.append(path)
 paths=sorted(set(p for p in paths if pathlib.Path(p).exists()));paths=[p for p in paths if not any(p.startswith(q.rstrip('/')+'/') for q in paths if p!=q)]
 save('volume-map.json',volume_map);save('runtime-paths.json',paths)
 with tarfile.open(root/'files-and-config.tar.gz','w:gz') as tf:
  for path in paths:tf.add(path,arcname=path.lstrip('/'),filter=filt)
 report['capture_complete']=True;save('capture-report.json',report);print('Runtime configuration, file volumes and SQLite captured',flush=True)
finally:
 # Always restore recorded application state, including on capture failure.
 errors=[]
 for x in sorted(apps,key=lambda x:x['kind']!='StatefulSet'):
  try:scale([x],True)
  except Exception:errors.append(x['metadata']['name'])
 for c in cron['items']:
  try:k('-n','nigeria','patch','cronjob',c['metadata']['name'],'--type=merge','-p',json.dumps({'spec':{'suspend':c['spec'].get('suspend',False)}}))
  except Exception:errors.append(c['metadata']['name'])
 for unit in units:
  try:run(['systemctl','start',unit])
  except Exception:errors.append(unit)
 save('resume-report.json',{'errors':errors,'resumed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()});print('Recorded application state restored; errors:',len(errors),flush=True)
 if errors:raise RuntimeError('Some services require restart recovery')
print('Private capture ready: '+str(root),flush=True)
