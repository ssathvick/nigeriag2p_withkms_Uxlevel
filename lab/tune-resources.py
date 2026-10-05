import subprocess,json
for kind in ['sts','deploy']:
 resources=json.loads(subprocess.check_output(['kubectl','get',kind,'-n','nigeria','-o','json']))['items']
 for obj in resources:
  name=obj['metadata']['name']
  if 'postgresql' not in name:continue
  containers=[]
  for c in obj['spec']['template']['spec']['containers']:
   containers.append({'name':c['name'],'resources':{'requests':{'cpu':'250m','memory':'512Mi'},'limits':{'cpu':'2','memory':'2Gi'}}})
  subprocess.run(['kubectl','patch',kind,name,'-n','nigeria','--type','strategic','-p',json.dumps({'spec':{'template':{'spec':{'containers':containers}}}})],check=True)
