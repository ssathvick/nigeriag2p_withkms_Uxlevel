import sys,json
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;fixture=json.loads((root/'native-release-state.json').read_text());out={}
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute('SELECT record_name,household_head_name,functional_record_id FROM g2p_register_households WHERE internal_record_id=%s',(fixture['internal'],));out['approved_household']=q.fetchone();assert out['approved_household'][0]=='Amina Bello Household · Demonstration',out
  q.execute('SELECT approval_status,register_ingest_process_status,deduplication_status_vs_intake_forms,deduplication_status_vs_register FROM g2p_intake_form_submissions WHERE submission_id=%s',(fixture['submission_id'],));out['workflow']=q.fetchone();assert out['workflow'][:2]==('APPROVED','PROCESSED')
  q.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE '%dedup%'");out['dedup_tables']=[x[0] for x in q.fetchall()]
out['role_separation']={}
role=json.loads((root/'role-audit.json').read_text())['permissions']
for name in ['Intake Officer','Intake Validator']:
 out['role_separation'][name]=[p for n,p in role if n==name]
assert 'intakeSubmission:edit' not in out['role_separation']['Intake Validator']
assert 'intakeSubmission:approve' not in out['role_separation']['Intake Officer']
(root/'final-data-verification.json').write_text(json.dumps(out,indent=2,default=str));print(json.dumps(out,default=str))
