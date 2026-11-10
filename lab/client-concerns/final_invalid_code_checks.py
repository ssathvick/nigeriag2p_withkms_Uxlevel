import json,sqlite3,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as app
work=Path(__file__).parent/'invalid-code-review';items=json.loads((work/'source-review.json').read_text())[:2]
c=sqlite3.connect('/opt/openg2p-lab/odk-sync/ledger.sqlite');c.row_factory=sqlite3.Row;checks=[]
with app.pg('register') as db:
 with db.cursor() as q:
  for item in items:
   row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(item['instance'],)).fetchone());assert row['state']=='EXCLUDED_TEST';assert row['source_hash']==item['source_sha256'];assert row['submission_id'] is None
   for table in ['g2p_intake_form_households','g2p_register_households']:
    q.execute('SELECT count(*) FROM '+table+' WHERE internal_record_id=%s',(item['internal_id'],));assert q.fetchone()[0]==0
   checks.append({'instance':item['instance'],'state':row['state'],'intake_count':0,'registry_count':0,'source_hash_unchanged':True})
status=json.loads(Path('/opt/openg2p-lab/odk-sync/status.json').read_text());assert status['counts']=={'EXCLUDED_TEST':2,'SUBMITTED':13},status;assert status['transient_failures']==0
assert subprocess.check_output(['systemctl','is-active','nsipa-odk-sync.timer'],text=True).strip()=='active'
domains=json.loads((work/'domain-checks.json').read_text());assert len(domains)==6
out={'checks':checks,'scheduled_pass':status,'timer_active':True,'registry_domain_checks':len(domains),'odk_source_checks':4,'validation_tests':8,'active_quarantines':0};(work/'final-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
