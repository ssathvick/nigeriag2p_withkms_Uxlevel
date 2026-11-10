import sys
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r,jos_connected as j
with r.LOCK:
 x=j.run(r,'JOS-NATIVE-003');l,details=j.calculation(r,x)
 j.ensure(not x['dispatch_started'] and not x['awe_id'] and l['list_workflow_status']=='initiated','Do not replace an authorised list.')
 j.ensure(len(details)==2,'Expected the observed unsent scoping fixture.')
 pb=r.Odoo('pbms-odoo','pbmsdb')
 pb.call('g2p.beneficiary.list','write',[[x['list_id']],{'brief':'SUPERSEDED UNSENT TEST: two-household scope caught by release guard. Never approved for payment. Replaced with per-household scoped list.'}])
 r.execute('UPDATE jos_runs SET list_id=NULL WHERE id=?',(x['id'],));j.event(r,x['id'],'authorized-synthetic-demo-setup','unapproved_list_12_superseded_due_to_scope_guard')
 j.operate(r,x['id'],'calculate','authorized-synthetic-demo-setup')
 print('Unsent list retained for audit; newly scoped native calculation queued.')
