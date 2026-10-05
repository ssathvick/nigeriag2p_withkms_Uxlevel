import sys,json,subprocess,base64
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
mapping=[('awe_user','awe-db-user','awe-db-user-password'),('consent_manager_user','consent-manager-db','consent-manager-db-user'),('superset','superset-db-user','superset-db-user-password')]
deployments=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy','-o','json']))['items']
for d in deployments:
 for c in d['spec']['template']['spec']['containers']:
  env={e['name']:e for e in c.get('env',[])}
  for key,e in env.items():
   if not key.endswith('_DB_USERNAME'):continue
   if env.get(key[:-8]+'HOSTNAME',{}).get('value')!='commons-postgresql':continue
   p=env.get(key[:-8]+'PASSWORD',{})
   ref=p.get('valueFrom',{}).get('secretKeyRef')
   if ref and e.get('value') and e['value']!='postgres':
    record=(e['value'],ref['name'],ref['key'])
    if record not in mapping:mapping.append(record)
for role,secret,key in mapping:
 if query('postgres',"SELECT 1 FROM pg_roles WHERE rolname='"+role+"';").strip()!='1':raise RuntimeError('Missing expected role '+role)
 data=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret',secret,'-o','json']))
 password=base64.b64decode(data['data'][key]).decode()
 query('postgres','ALTER ROLE "'+role+'" PASSWORD '+"'"+password.replace("'","''")+"';")
 print('Synced supporting database role:',role)
