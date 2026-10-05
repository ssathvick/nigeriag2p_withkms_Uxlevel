import json,subprocess,base64
def sql(service,db,q):
 secret=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','secret',service,'-o','json']))
 pw=base64.b64decode(secret['data']['postgres-password']).decode()
 p=subprocess.run(['kubectl','-n','nigeria','exec','-i','svc/'+service,'--','env','PGPASSWORD='+pw,'psql','-U','postgres','-d',db,'-At','-v','ON_ERROR_STOP=1'],input=q,text=True,capture_output=True)
 if p.returncode:raise RuntimeError('URL migration failed for '+db)
 return p.stdout
def quote(s):return '"'+s.replace('"','""')+'"'
targets=[('commons-postgresql',db) for db in ['iam','partner_management','consent_manager','register','awe','superset','odkdb']]+[('portal-backend-postgresql','portalpbmsdb')]
for service,db in targets:
 cols=sql(service,db,"select table_schema||'|'||table_name||'|'||column_name from information_schema.columns where table_schema not in ('pg_catalog','information_schema') and data_type in ('text','character varying') and (column_name like '%url%' or column_name like '%endpoint%' or column_name like '%issuer%' or column_name like '%redirect%' or column_name in ('jwks_uri','validation_endpoint')); ")
 count=0
 for line in cols.splitlines():
  schema,table,col=line.split('|');qualified=quote(schema)+'.'+quote(table);c=quote(col)
  q=f"UPDATE {qualified} SET {c}=replace(replace({c},'beneficiary.openg2p-ux.localhost','beneficiary.nigeriag2p.com'),'.openg2p.localhost','.nigeriag2p.com') WHERE {c} LIKE '%openg2p.localhost%' OR {c} LIKE '%openg2p-ux.localhost%';"
  result=sql(service,db,q)
  if result.strip()!='UPDATE 0':count+=1
 print(db,'updated URL columns',count)
