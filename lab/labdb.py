import subprocess,json,base64,os
def query(database,sql,host_service='commons-postgresql',secret_name='commons-postgresql',key='postgres-password',user='postgres'):
    secret=json.loads(subprocess.check_output(['kubectl','get','secret',secret_name,'-n','nigeria','-o','json']))
    ip=subprocess.check_output(['kubectl','get','svc',host_service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    env=dict(os.environ,PGPASSWORD=base64.b64decode(secret['data'][key]).decode())
    r=subprocess.run(['psql','-X','-h',ip,'-U',user,'-d',database,'-A','-t','-v','ON_ERROR_STOP=1'],input=sql,text=True,capture_output=True,env=env)
    if r.returncode:raise RuntimeError(r.stderr)
    return r.stdout
if __name__=='__main__':
    for db in ['awe','register','master_data','bridge_db']:
        print(db,query(db,"SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;"))
