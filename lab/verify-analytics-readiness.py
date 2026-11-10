"""Read current aggregate measures and retain sanitized review evidence."""
import sys,json,subprocess,hashlib
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
from flask import g
out=Path('/mnt/h/Nigeria_Mosip/codex/outputs/analytics_readiness');out.mkdir(exist_ok=True)
with r.app.test_request_context('/registration/api/analytics'):
 g.user={'sub':'readiness-review','roles':['iqs-programme-supervisor']};g.staff=False;g.session={'mode':'staff'};g.sid='readiness-read-only'
 report=r.app.view_functions['analytics.api']()
 data={k:report[k] for k in ['generated_at','filters','tracking_started_at','operations','knowledge','snapshots']}
 data['sources']=[{k:s[k] for k in ['source','refreshed_at','last_attempt','error','stale']} for s in report['sources']]
 data['count_checks']={'profiles_match':report['operations']['profiles']==r.one('SELECT COUNT(*) n FROM profiles')['n'],'published_match':report['knowledge']['live']==r.one("SELECT COUNT(*) n FROM km_articles WHERE published IS NOT NULL AND status!='archived'")['n']}
result=subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/test-analytics.py'],capture_output=True,text=True)
data['automated_tests']={'passed':result.returncode==0,'output':result.stdout+result.stderr}
assert result.returncode==0 and all(data['count_checks'].values())
data['source_hash_match']=hashlib.sha256(Path('/opt/openg2p-lab/registration/platform_analytics.py').read_bytes()).hexdigest()==hashlib.sha256(Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/platform_analytics.py').read_bytes()).hexdigest()
(out/'engineering-evidence.json').write_text(json.dumps(data,indent=2))
print(json.dumps({'tests':'8 passed','counts_reconciled':data['count_checks'],'sources':data['sources']}))
