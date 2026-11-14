import datetime,json,subprocess,sys
from pathlib import Path
def run(*args,input=None):return subprocess.run(args,input=input,text=True,capture_output=True,check=True).stdout
image=sys.argv[1] if len(sys.argv)>1 else 'nsipa/master-registry:meeting-20261112';tar='/tmp/native-registry-meeting.tar'
run('docker','save','-o',tar,image);run('k3s','ctr','images','import',tar)
d=json.loads(run('kubectl','-n','nigeria','get','deploy','register-staff-portal-ui','-o','json'))
backup=Path('/opt/openg2p-lab/registration/native-meeting-backups')/('ui-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(parents=True,mode=0o700);(backup/'deployment.json').write_text(json.dumps(d))
c=d['spec']['template']['spec']['containers'][0];c['image']=image;c['imagePullPolicy']='IfNotPresent'
d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['native-meeting-release']=datetime.datetime.now().isoformat()
run('kubectl','replace','-f','-',input=json.dumps(d));print(json.dumps({'native_ui':image,'backup':str(backup)}))
