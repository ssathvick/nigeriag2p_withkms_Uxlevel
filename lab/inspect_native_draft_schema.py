from test_mbr_db_connection import connect
with connect() as c:
 with c.cursor() as q:
  for t in ['g2p_intake_form_submissions','g2p_intake_form_households']:
   q.execute('select column_name,data_type,is_nullable,column_default from information_schema.columns where table_name=%s order by ordinal_position',(t,));print(t,q.fetchall())
  q.execute("select form_id,register_id,submission_source,draft_status,approval_status,created_by from g2p_intake_form_submissions limit 1");print('template',q.fetchone())
  q.execute("select payload from g2p_mbr_submissions where native_origin is null");p=q.fetchone()[0];print('empty draft',all(v in ('',None,[],{}) for v in p.values()),'types',{k:type(v).__name__ for k,v in p.items()})
