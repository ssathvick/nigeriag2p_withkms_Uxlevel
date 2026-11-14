import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
with r.pg('bridge_db') as c:
 with c.cursor() as q:
  q.execute('SELECT id,benefit_program_id,disbursement_cycle_id,number_of_disbursements,total_disbursement_quantity FROM disbursement_envelopes WHERE benefit_program_mnemonic=%s',('IQS_INTEGRATED_JOS_CCT_DEMO',));print('envelopes',q.fetchall())
  q.execute('SELECT d.id,d.beneficiary_id,d.disbursement_cycle_id,d.disbursement_quantity,b.fa_resolution_status,b.sponsor_bank_dispatch_status,b.sponsor_bank_dispatch_latest_error_code FROM disbursements d JOIN disbursement_envelopes e ON e.id=d.disbursement_envelope_id LEFT JOIN disbursement_batch_control b ON b.id=d.disbursement_batch_control_id WHERE e.benefit_program_mnemonic=%s',('IQS_INTEGRATED_JOS_CCT_DEMO',));print('instructions',q.fetchall())
pb=r.Odoo('pbms-odoo','pbmsdb');print(pb.call('g2p.beneficiary.list','read',[[10]],{'fields':['disbursement_batch_creation_status','dbc_number_of_attempts']}))
