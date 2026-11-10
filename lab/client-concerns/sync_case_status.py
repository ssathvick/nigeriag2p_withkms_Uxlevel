import sys,sqlite3,json
sys.path.insert(0,'/opt/openg2p-lab/registration');import registration_app as r
c=sqlite3.connect('/opt/openg2p-lab/odk-sync/ledger.sqlite');c.row_factory=sqlite3.Row
row=c.execute('SELECT * FROM imports WHERE instance_id=?',(sys.argv[1],)).fetchone()
out={'ledger':dict(row) if row else None}
if row and row['internal_id']:
 with r.pg('register') as db:
  with db.cursor() as q:
   q.execute('SELECT count(*) FROM g2p_intake_form_households WHERE internal_record_id=%s',(row['internal_id'],));out['intake_count']=q.fetchone()[0]
   q.execute('SELECT count(*) FROM g2p_register_households WHERE internal_record_id=%s',(row['internal_id'],));out['registry_count']=q.fetchone()[0]
print(json.dumps(out))
