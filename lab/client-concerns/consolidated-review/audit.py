import sys,json,sqlite3,datetime,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
w=Path(__file__).parent;physical=json.loads((w.parent/'physical-device-verification/state.json').read_text());out={'checked_at_ist':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat(),'records':[]}
with r.pg('register') as db:
 with db.cursor() as q:
  for key,s in physical.items():
   if not isinstance(s,dict) or 'mapping' not in s:continue
   internal=s['mapping']['payload']['internal_record_id']
   q.execute('select count(*) from g2p_intake_form_households where internal_record_id=%s',(internal,));a=q.fetchone()[0]
   q.execute('select functional_record_id from g2p_register_households where internal_record_id=%s',(internal,));rows=q.fetchall();assert a==1 and len(rows)==1
   out['records'].append({'reference':key,'intakes':a,'registry_records':len(rows),'functional_id':rows[0][0],'two_domain_checks':len(s['domains']),'zero_registry_after_first_review':s['afterFirstReview']['registry_count']==0})
out['sync']=json.loads(Path('/opt/openg2p-lab/odk-sync/status.json').read_text())
out['timer_active']=subprocess.check_output(['systemctl','is-active','nsipa-odk-sync.timer'],text=True).strip()
out['fault_relay_active']=subprocess.run(['systemctl','is-active','nsipa-phone-fault'],capture_output=True,text=True).stdout.strip()
assert out['timer_active']=='active' and out['fault_relay_active']=='inactive'
(w/'final-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
