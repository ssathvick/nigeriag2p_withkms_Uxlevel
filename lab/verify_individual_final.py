import json
from pathlib import Path
from test_individual_branches import OUT,detail,master,cr
from test_mbr_db_connection import connect
checks=[]
def load(n):return json.loads((OUT/(n+'.json')).read_text())
for name in ['returned','rejected','rejected-level2','change-rejected','change-rejected-level2','capture']:
 s=load(name);d=detail(s);row=master(s)
 if name in ['rejected','rejected-level2']:
  assert d['approval_status']=='REJECTED' and d['draft_status']=='FINAL' and not row
 else:assert d['approval_status']=='APPROVED' and row and row['functional_record_id']
 if name=='returned':assert row['estimated_age']==36 and sum(e['event_type']=='request_returned' for e in d['review_history'])==2
 if name=='capture':assert row['link_internal_record_id']==load('linked-household')['internal_id'] and row['estimated_age']==36
 if s.get('cr'):
  change=cr(s)
  with connect() as c:
   with c.cursor() as q:q.execute('SELECT estimated_age FROM g2p_register_history_individuals WHERE change_request_id=%s',(s['cr']['id'],));versions=q.fetchall()
  if name=='returned':assert versions==[(36,)] and change['current_register_data'][0]['estimated_age']==35
  else:assert change['approval_status']=='REJECTED' and not versions and row['estimated_age']==35
 checks.append({'case':name,'status':'passed','registration':d['approval_status'],'published':bool(row),'change_request':cr(s)['approval_status'] if s.get('cr') else None})
(OUT/'final-checks.json').write_text(json.dumps({'status':'passed','checks':checks},indent=2));print('PASS all six individual cases: final statuses, master values, linked household and exact change history')
