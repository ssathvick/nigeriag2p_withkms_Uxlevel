import tarfile,pathlib,yaml,subprocess
root=pathlib.Path('/opt/openg2p-lab/charts/legacy')
root.mkdir(exist_ok=True)
with tarfile.open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/upstream-helm/openg2p-pbms-2.0.3.tgz') as t:t.extractall(root,filter='data')
password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
values={'image':{'repository':'openg2p/openg2p-pbms-core','tag':'1.3.0'},'odooEmail':'admin@nigeria.openg2p.localhost','odooPassword':password,'odooDatabase':'portalpbmsdb','service':{'type':'ClusterIP','port':80},'ingress':{'enabled':False},'resources':{'requests':{'memory':'1Gi','cpu':'250m'},'limits':{'memory':'4Gi','cpu':'3'}},'postgresql':{'enabled':True,'image':{'registry':'docker.io','repository':'openg2p/postgresql','tag':'16.4.0-debian-12-r14'},'auth':{'username':'portaluser','database':'portalpbmsdb','password':password,'postgresPassword':password},'primary':{'resources':{'requests':{'memory':'512Mi','cpu':'250m'},'limits':{'memory':'2Gi','cpu':'2'}}}}}
pathlib.Path('/opt/openg2p-lab/portal-backend.yaml').write_text(yaml.safe_dump(values))
subprocess.run(['helm','upgrade','--install','portal-backend',str(root/'openg2p-pbms/charts/odoo'),'-n','nigeria','-f','/opt/openg2p-lab/portal-backend.yaml','--wait','--timeout','10m'],check=True,env=__import__('os').environ|{'KUBECONFIG':'/etc/rancher/k3s/k3s.yaml'})
