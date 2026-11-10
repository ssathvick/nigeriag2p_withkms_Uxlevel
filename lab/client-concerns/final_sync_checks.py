import sys,json,sqlite3,subprocess
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path(__file__).parent;work=root/'auto-sync-verification';state=json.loads((work/'state.json').read_text());assert state['finished']
c=sqlite3.connect('/opt/openg2p-lab/odk-sync/ledger.sqlite');c.row_factory=sqlite3.Row;results=[]
with r.pg('register') as db:
 with db.cursor() as q:
  for key,item in state.items():
   if not isinstance(item,dict) or 'mapping' not in item:continue
   row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(item['instance'],)).fetchone());assert row['state']=='SUBMITTED'
   q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(row['internal_id'],));assert q.fetchone()[0]==1
   q.execute('SELECT row_to_json(h) FROM g2p_register_households h WHERE internal_record_id=%s',(row['internal_id'],));records=q.fetchall();assert len(records)==1
   for field,value in item['mapping']['payload'].items():assert records[0][0][field]==value,(key,field)
   results.append({'case':key,'intake_count':1,'registry_count':1,'saved_fields_match':True,'functional_id':records[0][0]['functional_record_id']})
for item in json.loads((work/'replay-and-invalid.json').read_text()):
 if 'invalidNumericInstance' in item:
  row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(item['invalidNumericInstance'],)).fetchone());assert row['state']=='QUARANTINED';assert row['submission_id'] is None;results.append({'host':item['host'],'invalid_numeric':'QUARANTINED','created_intakes':0})
counts=dict(c.execute('SELECT state,count(*) FROM imports GROUP BY state').fetchall());errors=[dict(x) for x in c.execute("SELECT form_id,instance_id,state,error FROM imports WHERE state!='SUBMITTED'")]
assert subprocess.check_output(['systemctl','is-enabled','nsipa-odk-sync.timer'],text=True).strip()=='enabled'
assert subprocess.check_output(['systemctl','is-active','nsipa-odk-sync.timer'],text=True).strip()=='active'
status=json.loads(Path('/opt/openg2p-lab/odk-sync/status.json').read_text());assert status['transient_failures']==0
out={'checks':results,'ledger_counts':counts,'held_items':errors,'timer_enabled':True,'timer_active':True,'last_pass':status}
(work/'final-checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
