import subprocess,json,pathlib,os,datetime
root=pathlib.Path('/opt/openg2p-lab/baseline');root.mkdir(mode=0o700,exist_ok=True)
for kind in ['deploy,sts,svc,cm,secret,pvc,virtualservice,gateway','jobs']:
 data=subprocess.check_output(['kubectl','-n','nigeria','get',kind,'-o','yaml']);path=root/('jobs.yaml' if kind=='jobs' else 'resources.yaml');path.write_bytes(data);os.chmod(path,0o600)
pods=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','pods','-o','json']))['items']
images=sorted({(s['image'],s.get('imageID','')) for p in pods for s in p.get('status',{}).get('containerStatuses',[])})
env=os.environ|{'KUBECONFIG':'/etc/rancher/k3s/k3s.yaml'}
releases=json.loads(subprocess.check_output(['helm','list','-n','nigeria','-o','json'],env=env))
public={'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'images':[{'image':a,'digest':b} for a,b in images],'helm_releases':releases,'source_commits':{}}
folder=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
for child in folder.iterdir():
 if (child/'.git').is_dir():
  public['source_commits'][child.name]=subprocess.check_output(['git','-c','safe.directory='+str(child),'-C',str(child),'rev-parse','HEAD'],text=True).strip()
(folder/'installed-versions.json').write_text(json.dumps(public,indent=2))
pathlib.Path(root/'nginx.conf').write_text(pathlib.Path('/etc/nginx/sites-available/openg2p-lab').read_text())
for name in ['registry-inspect','registry-partner-inspect','portal-inspect','seed-inspect']:
 subprocess.run(['kubectl','-n','nigeria','delete','pod',name,'--ignore-not-found=true'],check=True)
name='commons-services-keycloak-init-3-52417914'
r=subprocess.run(['kubectl','-n','nigeria','logs','job/'+name],capture_output=True)
(root/'superseded-keycloak-init.log').write_bytes(r.stdout+r.stderr);os.chmod(root/'superseded-keycloak-init.log',0o600)
subprocess.run(['kubectl','-n','nigeria','delete','job',name,'--ignore-not-found=true'],check=True)
print('Private baseline and public image/source inventory saved. Temporary inspection workloads removed.')
