import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
sid='718cc3ad-7f81-46cb-aea0-2696bb15e732';rid='e6cb6931-b0bb-43cf-9761-b3dda5828c50'
with r.pg('register') as c:
 with c.cursor() as q:
  q.execute('SELECT record_name,household_head_name,created_at,last_approved_at FROM g2p_register_households WHERE internal_record_id=%s',(rid,));row=q.fetchone();assert row and row[1]=='Amina Bello' and row[3];print('Confirmed approved synthetic registry row:',row)
  q.execute("UPDATE g2p_intake_form_submissions SET register_ingest_process_status='PROCESSED',register_ingest_process_last_error_code=NULL WHERE submission_id=%s AND approval_status='APPROVED' AND draft_status='FINAL' AND register_ingest_process_status IN ('FAILED','PENDING')",(sid,));print('Reconciled own test status after duplicate retry:',q.rowcount)
 c.commit()
