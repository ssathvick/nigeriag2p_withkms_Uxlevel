import sys
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
sid='718cc3ad-7f81-46cb-aea0-2696bb15e732'
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute('SELECT approval_status,register_ingest_process_status,register_ingest_process_last_error_code FROM g2p_intake_form_submissions WHERE submission_id=%s',(sid,))
  row=q.fetchone();print(row)
  if row and row[0]=='APPROVED' and row[1]=='FAILED':
   q.execute("UPDATE g2p_intake_form_submissions SET register_ingest_process_status='PENDING' WHERE submission_id=%s AND approval_status='APPROVED' AND register_ingest_process_status='FAILED'",(sid,));print('Requeued only the synthetic verification submission')
 c.commit()
