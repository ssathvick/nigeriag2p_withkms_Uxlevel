import sys,json,subprocess,ast
from pathlib import Path
root=Path(__file__).parent/'meeting-native';deployment,suffix=sys.argv[1:3];changes=json.loads((root/'changes.json').read_text())[deployment]
source,target=next((s,t) for s,t in changes.items() if t.endswith(suffix));value=(root/source).read_text();ast.parse(value)
def run(*args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
d=json.loads(run('kubectl','-n','nigeria','get','deploy',deployment,'-o','json'));spec=d['spec']['template']['spec'];mount=next(m for m in spec['containers'][0]['volumeMounts'] if m['mountPath']==target);volume=next(v for v in spec['volumes'] if v['name']==mount['name']);cm=json.loads(run('kubectl','-n','nigeria','get','cm',volume['configMap']['name'],'-o','json'));cm['data'][mount['subPath']]=value
run('kubectl','replace','-f','-',input=json.dumps(cm));run('kubectl','-n','nigeria','rollout','restart','deploy/'+deployment);print('Updated',deployment,suffix)
