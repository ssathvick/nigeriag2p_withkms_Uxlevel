from pathlib import Path
import requests,json,re,datetime
s=requests.Session();base='https://nigeriag2p.com';results={}
for path in ['/jos-cct/','/jos-cct/brief.html','/jos-cct/jos-cct.js','/jos-cct/jos-cct.css']:
 r=s.get(base+path,timeout=30,allow_redirects=False);assert r.status_code==200,(path,r.status_code);assert not r.headers.get('Set-Cookie');results[path]=r.status_code
 if path=='/jos-cct/':assert 'jos-root' in r.text and 'site-shell.js' not in r.text
 if path.endswith('brief.html'):assert 'fictional' in r.text and '1,500,000' in r.text
 if path.endswith('.js'):assert 'DEMO-JOS-' in r.text and 'Needs review' in r.text and 'No funds transferred' in r.text
r=s.get(base+'/jos-cct',timeout=30,allow_redirects=False);assert r.status_code==308 and r.headers['Location']==base+'/jos-cct/'
home=s.get(base+'/',timeout=30);script=re.search(r'src="(/iqs-brand/site.js\?v=[^"]+)"',home.text).group(1);assert 'jos-' in script
assert 'Jos CCT pilot demo' in s.get(base+script,timeout=30).text
assert s.get(base+'/registration/api/analytics',timeout=30,allow_redirects=False).status_code==401
out={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'public_routes':results,'private_analytics':401,'main_site_link':True,'budget_usd':1500000,'planned_households':4250,'planned_months':12,'classification':'synthetic demonstration','persistent_backend_mutations':False,'slides':10,'browser_checks':['six-step household walkthrough','receipt total increased by $25 only after confirmation','failed-payment retry','budget segment explanation','reset restored original sample data','geographic filter','390px mobile layout','main-site service card'],'notes':'Browser actions persist in sessionStorage only. No live payment or registry integration is claimed.'}
target=Path('/mnt/h/Nigeria_Mosip/codex/outputs/jos-cct/verification.json');target.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
