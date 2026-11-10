"""Non-invasive checks against this sandbox's known endpoints only."""
import concurrent.futures,datetime as dt,json,time
from pathlib import Path
import requests
BASE='https://g2p.wverve.in/registration'
checks={}
for path,expected in [('/api/workspace',401),('/api/analytics',401),('/api/simulation/report',401),('/api/phase1/report',401),('/api/phase1/context',401),('/api/phase1/readiness',401),('/api/phase1/conditionality',401),('/phase1/conditionality',401),('/phase1/cms',401),('/phase1/field',401),('/api/phase1/public-data',200)]:
 res=requests.get(BASE+path,timeout=15,allow_redirects=False)
 checks[path]={'http_status':res.status_code,'expected':expected,'status':'passed' if res.status_code==expected else 'failed'}
portal=requests.get(BASE+'/phase1/portal',timeout=15)
checks['security_headers']={'status':'passed' if "frame-ancestors 'none'" in portal.headers.get('Content-Security-Policy','') and portal.headers.get('X-Content-Type-Options')=='nosniff' else 'failed'}
cookie=portal.headers.get('Set-Cookie','')
checks['session_cookie_flags']={'secure':'Secure' in cookie,'http_only':'HttpOnly' in cookie,'same_site_lax':'SameSite=Lax' in cookie}
res=requests.post(BASE+'/phase1/grievances',data={'household':'DEMO-HH-01','channel':'web','reason':'payment_delay'},timeout=15,allow_redirects=False)
checks['unauthenticated_write_and_csrf']={'http_status':res.status_code,'status':'passed' if res.status_code==403 else 'failed'}
origin=requests.get(BASE+'/api/phase1/public-data',headers={'Origin':'https://example.invalid'},timeout=15)
checks['no_arbitrary_cors_origin']={'status':'passed' if 'Access-Control-Allow-Origin' not in origin.headers else 'failed'}
def timing(index):
 start=time.perf_counter();resp=requests.get(BASE+'/phase1/portal?lang='+('en','ha','yo','ig')[index%4],timeout=15);return {'status':resp.status_code,'seconds':time.perf_counter()-start}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:samples=list(pool.map(timing,range(24)))
times=sorted(x['seconds'] for x in samples)
report={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Known public sandbox endpoint access, headers and 24 HTTP requests at concurrency 6','checks':checks,'http_response_p95_seconds':round(times[int(.95*(len(times)-1))],3),'http_response_max_seconds':round(max(times),3),'responses_200':sum(x['status']==200 for x in samples),'limitations':['HTTP response time is not full browser page-load time','This focused regression review is not an independent penetration test or WCAG certificate']}
report['status']='passed' if all(x.get('status','passed')=='passed' for x in checks.values()) and all(checks['session_cookie_flags'].values()) and all(x['status']==200 for x in samples) and max(times)<3 else 'needs_review'
Path(__file__).with_name('phase1-evidence').joinpath('public-security-performance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
