"""Aggregate engineering evidence and conservative availability sampling."""
import datetime as dt,json,math
from pathlib import Path
import requests
from flask import Blueprint,g,abort,render_template

def install(r,db):
 bp=Blueprint('phase1_observability',__name__)
 with db() as c:c.execute('CREATE TABLE IF NOT EXISTS health_samples(id INTEGER PRIMARY KEY,at TEXT NOT NULL,probe TEXT NOT NULL,status INTEGER NOT NULL,elapsed_ms REAL NOT NULL)')
 def collect():
  for label,url in [('origin','http://127.0.0.1:18081'+r.PREFIX+'/health'),('public',r.BASE+r.PREFIX+'/phase1/portal')]:
   start=__import__('time').perf_counter();status=0
   try:status=requests.get(url,timeout=5,allow_redirects=False).status_code
   except requests.RequestException:pass
   elapsed=(__import__('time').perf_counter()-start)*1000
   with db() as c:c.execute('INSERT INTO health_samples(at,probe,status,elapsed_ms) VALUES(?,?,?,?)',(r.stamp(),label,status,elapsed))
 def require():
  r.require_user()
  if g.session.get('mode')!='staff' or not set(g.user.get('roles',[])).intersection({'iqs-intake-reviewer','iqs-programme-supervisor'}):abort(403,'Readiness evidence requires a sandbox supervisor or reviewer.')
 def summary():
  # Only approved non-sensitive technical summaries are read, never credentials/contracts.
  folder=r.ROOT/'phase1-evidence';evidence={}
  for name in ['automated-tests','native-registration-uat','native-reconciliation-uat','native-household-payment','native-mapper-guard-tests','native-bank-replay','native-statement-recovery','native-statement-backlog','native-programme-concurrency','capacity-agents','capacity-native-registry','public-security-performance','browser-readiness']:
   path=folder/(name+'.json')
   if path.is_file():
    try:evidence[name]=json.loads(path.read_text())
    except (ValueError,OSError):evidence[name]={'status':'unavailable'}
  with db() as c:samples=[dict(x) for x in c.execute("SELECT at,status,elapsed_ms FROM health_samples WHERE probe='public' ORDER BY id")]
  availability={'samples':len(samples),'certified':False,'notice':'An agreed observation window and independent review are required for SLA sign off.'}
  if samples:
   buckets={}
   for sample in samples:
    minute=dt.datetime.fromisoformat(sample['at']).replace(second=0,microsecond=0)
    buckets.setdefault(minute,[]).append(sample['status'])
   start=min(buckets);closed=dt.datetime.now(dt.timezone.utc).replace(second=0,microsecond=0)-dt.timedelta(minutes=1)
   end=max(closed,max(buckets));expected=int((end-start).total_seconds()/60)+1
   success=sum(all(status==200 for status in values) for values in buckets.values())
   availability.update(started_at_utc=samples[0]['at'],expected_minutes=expected,successful_minutes=success,distinct_sample_minutes=len(buckets),observed_availability_percent=round(100*success/expected,3),missing_or_failed_samples=expected-success)
  household=evidence.get('native-household-payment',{});capacity=evidence.get('capacity-native-registry',{})
  metrics=[('Automated test executions',sum(x.get('tests') or 0 for x in evidence.get('automated-tests',{}).get('suites',[]))),('Native fictional instructions reconciled',household.get('all_reconciled_instructions','Pending')),('Native reconciliation exceptions',household.get('reconciliation_exceptions','Pending')),('Verified local household credit NGN',household.get('local_account_balance_ngn','Pending')),('Separate native registry SQL benchmark records',capacity.get('verified_records','Running or pending'))]
  return {'scope':'Sandbox technical verification only; formal NSIPA UAT and Phase 1 acceptance remain pending','metrics':metrics,'evidence':evidence,'availability':availability}
 @bp.get(r.PREFIX+'/phase1/readiness')
 def page():require();return r.page('phase1-readiness.html',readiness=summary())
 @bp.get(r.PREFIX+'/api/phase1/readiness')
 def api():require();return summary()
 r.app.register_blueprint(bp);r.phase1_monitor=collect
