from pathlib import Path
import subprocess,json,datetime,time,concurrent.futures,requests
src=Path(__file__).parent;out=src/'kms-ux-evidence';out.mkdir(exist_ok=True)
results=[]
for name in ['test-kms-readiness.py','test-local-ai.py','test-persona-workspaces.py']:
 p=subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python',str(src/name)],capture_output=True,text=True)
 results.append({'suite':name,'passed':p.returncode==0,'output':p.stdout+p.stderr})
 assert p.returncode==0,p.stderr
def sample(i):
 start=time.perf_counter();response=requests.get('https://g2p.wverve.in/registration/knowledge?q=household+registration',timeout=20)
 return {'status':response.status_code,'seconds':round(time.perf_counter()-start,4),'no_store':'no-store' in response.headers.get('Cache-Control',''),'matches':'12 matching entries' in response.text}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:checks=list(pool.map(sample,range(24)))
assert all(a['status']==200 and a['no_store'] and a['matches'] for a in checks)
data={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'suites':results,'http_samples':checks,'http_p95_seconds':sorted(a['seconds'] for a in checks)[22],'scope':'HTTP timings, not browser loading, WCAG certification or client acceptance. Inherited KMS cases repeat in two suites.'}
(out/'engineering-results.json').write_text(json.dumps(data,indent=2))
print(json.dumps({'suites_passed':len(results),'http_responses':len(checks),'http_p95_seconds':data['http_p95_seconds']}))
