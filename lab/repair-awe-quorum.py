import subprocess,json
name='commons-services-awe';path='/usr/local/lib/python3.13/site-packages/awe/services/engine.py'
code=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+name,'--','cat',path],text=True)
code=code.replace('approver_tasks = [t for t in stage_tasks if t.kind == "approver"]','approver_tasks = [t for t in stage_tasks if t.kind == "approver" and t.status != "reassigned"]')
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'awe-quorum-repair','namespace':'nigeria'},'data':{'engine.py':code}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True)
d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',name,'-o','json']));s=d['spec']['template']['spec'];c=s['containers'][0]
s['volumes']=[v for v in s.get('volumes',[]) if v['name']!='awe-quorum-repair']+[{'name':'awe-quorum-repair','configMap':{'name':'awe-quorum-repair'}}]
c['volumeMounts']=[v for v in c.get('volumeMounts',[]) if v['name']!='awe-quorum-repair']+[{'name':'awe-quorum-repair','mountPath':path,'subPath':'engine.py','readOnly':True}]
subprocess.run(['kubectl','-n','nigeria','patch','deploy',name,'--type=merge','-p',json.dumps({'spec':{'template':d['spec']['template']}})],check=True,stderr=subprocess.DEVNULL)
