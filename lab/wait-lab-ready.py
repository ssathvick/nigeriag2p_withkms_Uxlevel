"""Wait for real workload readiness and HTTPS routes before opening the user's browser."""
import subprocess,json,time,pathlib,re,sys
deadline=time.monotonic()+1200
lab=pathlib.Path('/opt/openg2p-lab')
def run(args,timeout=25):
 return subprocess.run(args,capture_output=True,text=True,timeout=timeout)
def diagnostics():
 for args in [['systemctl','--no-pager','status','k3s','nginx','openg2p-lab-network'],['kubectl','-n','nigeria','get','pods'],['journalctl','-u','openg2p-lab-network','--no-pager','-n','25']]:
  try:
   r=run(args);print(r.stdout[-14000:],r.stderr[-1000:],flush=True)
  except Exception as e: print(type(e).__name__,flush=True)
while time.monotonic()<deadline:
 try:
  services=run(['systemctl','is-active','k3s','nginx','openg2p-lab-network'])
  resource=run(['kubectl','-n','nigeria','get','deployments,statefulsets','-o','json'])
  if resource.returncode:
   print('Waiting for Kubernetes to start...',flush=True)
  else:
   items=json.loads(resource.stdout)['items']
   waiting=[]
   for item in items:
    spec=item['spec'];status=item.get('status',{});expected=spec.get('replicas',1)
    if status.get('observedGeneration',0)<item['metadata'].get('generation',1) or status.get('readyReplicas',0)!=expected or (item['kind']=='Deployment' and status.get('updatedReplicas',0)!=expected):
     waiting.append(item['metadata']['name'])
   print(f'Services ready: {len(items)-len(waiting)}/{len(items)}'+(' | Waiting: '+', '.join(waiting[:6]) if waiting else ''),flush=True)
   if items and not waiting and services.returncode==0:
    home=(lab/'home/index.html').read_text()
    urls=list(dict.fromkeys(['https://openg2p.localhost/']+re.findall(r'href="(https://[^" ]+)"',home)))
    failed=[]
    for url in urls:
     host=url.split('/')[2]
     response=run(['curl','-sS','-o','/dev/null','-w','%{http_code}','--max-time','8','--cacert',str(lab/'tls/ca.crt'),'--resolve',host+':443:127.0.0.1',url],timeout=10)
     if response.returncode or response.stdout not in ['200','301','302','303','307','308']:failed.append(host)
    if not failed:
     print(f'All {len(items)} workloads and {len(urls)} HTTPS entry points are ready.',flush=True)
     sys.exit(0)
    print('Waiting for HTTPS routes: '+', '.join(failed),flush=True)
 except (subprocess.TimeoutExpired,json.JSONDecodeError,OSError) as e:
  print('Waiting for startup: '+type(e).__name__,flush=True)
 time.sleep(10)
print('Startup timed out after 20 minutes. Diagnostic information:',flush=True)
diagnostics()
sys.exit(1)
