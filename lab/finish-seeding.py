import subprocess,json,yaml
def get(kind,name):return json.loads(subprocess.check_output(['kubectl','get',kind,name,'-n','nigeria','-o','json']))
def apply(obj):subprocess.run(['kubectl','apply','-f','-'],input=yaml.safe_dump(obj),text=True,check=True,stdout=subprocess.DEVNULL)
source=get('secret','master-data')
apply({'apiVersion':'v1','kind':'Secret','metadata':{'name':'master-data-db','namespace':'nigeria'},'type':'Opaque','data':source['data']})
for original,new in [('register-db-seed','nigeria-register-seed'),('commons-services-mock-identity-system-identity-seed','nigeria-identity-seed')]:
    exists=subprocess.run(['kubectl','get','job',new,'-n','nigeria'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    if exists:print(new,'already exists');continue
    job=get('job',original)
    spec=job['spec'];spec.pop('selector',None);spec.pop('manualSelector',None)
    spec['template']['metadata']={'labels':{'app':'nigeria-lab-seed'}}
    if original=='register-db-seed':
        for c in spec['template']['spec']['containers']:
            for e in c.get('env',[]):
                if e['name'] in ['SYNC_GEO_WIDGETS','LOAD_SAMPLE_DATA','LOAD_IMAGES']:e['value']='true'
    apply({'apiVersion':'batch/v1','kind':'Job','metadata':{'name':new,'namespace':'nigeria'},'spec':spec})
    print(new,'started')
