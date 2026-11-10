import json,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).parent
def run(args,**kw):
 r=subprocess.run(args,text=True,capture_output=True,**kw)
 if r.returncode:raise RuntimeError(r.stderr[-1500:])
 return r.stdout
def deploy(deployment,name,files):
 backup=Path((ROOT/'backup-location.txt').read_text());d=json.loads(run(['kubectl','-n','nigeria','get','deploy',deployment,'-o','json']))
 p=backup/(deployment+'-'+name+'.json')
 if not p.exists():p.write_text(json.dumps(d))
 data={f'f{i}':value for i,value in enumerate(files.values())};cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':name,'namespace':'nigeria'},'data':data}
 run(['kubectl','apply','--server-side','--field-manager=nsipa-client-concerns','-f','-'],input=json.dumps(cm))
 spec=d['spec']['template']['spec'];container=spec['containers'][0];spec['volumes']=[v for v in spec.get('volumes',[]) if v['name']!=name]+[{'name':name,'configMap':{'name':name}}]
 container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['name']!=name and v['mountPath'] not in files]+[{'name':name,'mountPath':path,'subPath':f'f{i}','readOnly':True} for i,path in enumerate(files)]
 d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})[name+'-sha']=hashlib.sha256(json.dumps(data).encode()).hexdigest()
 run(['kubectl','replace','-f','-'],input=json.dumps(d));print('Deployed',name,'to',deployment)
