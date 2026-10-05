import subprocess,json,pathlib,datetime,re
root=pathlib.Path('/opt/openg2p-lab');checks=[]
for kind in ['deployments','statefulsets']:
 for item in json.loads(subprocess.check_output(['kubectl','-n','nigeria','get',kind,'-o','json']))['items']:
  expected=item['spec'].get('replicas',1);ready=item.get('status',{}).get('readyReplicas',0)
  checks.append({'type':kind,'name':item['metadata']['name'],'ready':ready,'expected':expected,'passed':ready==expected})
html=(root/'home/index.html').read_text();urls=list(dict.fromkeys(['https://openg2p.localhost']+re.findall(r'href="(https://[^" ]+)"',html)))
for url in urls:
 host=url.split('/')[2]
 r=subprocess.run(['curl','--silent','--show-error','--output','/dev/null','--write-out','%{http_code}','--max-time','20','--cacert',str(root/'tls/ca.crt'),'--resolve',host+':443:127.0.0.1',url],text=True,capture_output=True)
 checks.append({'type':'https','url':url,'status':r.stdout,'passed':r.returncode==0 and r.stdout in ['200','301','302','303','307','308']})
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'passed':all(c['passed'] for c in checks)}
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/health-report.json').write_text(json.dumps(report,indent=2))
for c in checks:
 if not c['passed']:print('FAILED',c)
print('Ready workloads:',sum(c['passed'] for c in checks if c['type']!='https'),'/',sum(c['type']!='https' for c in checks))
print('HTTPS entry points:',sum(c['passed'] for c in checks if c['type']=='https'),'/',len(urls))
print('Overall:',report['passed'])
