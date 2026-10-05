import pathlib,subprocess,yaml,json,sys,os
root=pathlib.Path('/opt/openg2p-lab');workspace=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
password=yaml.safe_load((root/'credentials.yaml').read_text())['admin_password']
for folder,dirs,files in os.walk(workspace):
 dirs[:]=[d for d in dirs if d not in ['.git','node_modules','__pycache__']]
 for name in files:
  path=pathlib.Path(folder)/name
  if password.encode() in path.read_bytes():raise RuntimeError('Private credential found in workspace file: '+str(path))
backups=sorted(p for p in (root/'backups').iterdir() if p.is_dir())
latest=backups[-1]
for service in ['commons-postgresql','pbms-postgresql','registry-postgresql','example-bank-postgresql','portal-backend-postgresql']:
 path=latest/(service+'.sql');assert path.stat().st_size>10000,path
 text=path.read_text();assert 'PostgreSQL database cluster dump complete' in text,path
assert (latest/'files-and-config.tar.gz').stat().st_size>1000
sys.path.insert(0,str(workspace));from labdb import query
assert query('register',"SELECT count(*) FROM g2p_register_individuals;").strip()=='12'
assert query('awe',"SELECT status FROM approval_request WHERE id='700ca35f-d97d-4f6d-84e5-3be9d3a75049';").strip()=='approved'
assert query('bridge_db','SELECT count(*) FROM disbursements;').strip()=='6'
assert query('bgtaskdb',"SELECT disbursement_status FROM disbursement_batch WHERE id='d3d3291c-9a95-43d8-8272-d2dc40d7a37c';",host_service='pbms-postgresql',secret_name='pbms-postgresql').strip()=='complete'
subprocess.run(['python3',str(workspace/'smoke-check.py')],check=True)
assert json.loads((workspace/'health-report.json').read_text())['passed']
print('Backup contents, credential separation, persisted records, approved workflow and signed Bridge batch verified.')
print('Latest private backup:',latest)
