import sys,json,sqlite3,fcntl
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
root=Path('/opt/openg2p-lab/odk-sync');instance='uuid:45c389db-654f-47be-b4f4-7d0b4e2b0c74'
with open(root/'worker.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);c=sqlite3.connect(root/'ledger.sqlite');c.row_factory=sqlite3.Row;row=dict(c.execute('SELECT * FROM imports WHERE instance_id=?',(instance,)).fetchone());assert row['state']=='CREATE_UNCERTAIN' and row['submission_id'] is None
 with r.pg('register') as db:
  with db.cursor() as q:
   q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(row['internal_id'],));assert q.fetchone()[0]==0
   q.execute('SELECT count(*) FROM g2p_register_households WHERE internal_record_id=%s',(row['internal_id'],));assert q.fetchone()[0]==0
   q.execute('SELECT count(*) FROM g2p_intake_form_submissions WHERE submission_id=%s',('72dae4aa-f80e-4d8a-af2f-a75a1787ab74',));assert q.fetchone()[0]==0
 audit={'instance':instance,'previous_state':row,'reason':'Native log confirmed unique application-reference violation and transaction rollback. API deployment restarted after reference-format fix. Both deterministic record and failed submission UUID are absent. Authorized scoped retry after reconciliation.','intake_count':0,'registry_count':0,'failed_submission_count':0}
 (Path(__file__).parent/'legacy-verification/create-reconciliation.json').write_text(json.dumps(audit,indent=2))
 c.execute("UPDATE imports SET state='DISCOVERED',error=NULL WHERE instance_id=?",(instance,));c.commit();c.close()
print('Reconciled rolled-back create; released exactly one source for safe retry.')
