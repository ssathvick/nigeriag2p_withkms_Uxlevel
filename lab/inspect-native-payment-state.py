import json,sys
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
report={'scope':'Native synthetic payment state; read-only'}
with r.pg('bridge_db') as c:
 with c.cursor() as cur:
  cur.execute('SELECT fa_resolution_status,sponsor_bank_dispatch_status,COUNT(*) FROM disbursement_batch_control GROUP BY fa_resolution_status,sponsor_bank_dispatch_status');report['batches']=[list(x) for x in cur.fetchall()]
  for table in ['disbursement_envelopes','disbursements','disbursement_recons','disbursement_error_recons']:
   cur.execute('SELECT COUNT(*) FROM '+table);report[table]=cur.fetchone()[0]
  cur.execute('SELECT DISTINCT fa_resolution_latest_error_code,sponsor_bank_dispatch_latest_error_code FROM disbursement_batch_control');report['error_codes']=[list(x) for x in cur.fetchall()]
  cur.execute('SELECT id,benefit_program_id,benefit_code_id,benefit_program_mnemonic,total_disbursement_quantity,measurement_unit FROM disbursement_envelopes');report['envelopes']=[list(x) for x in cur.fetchall()]
  cur.execute('SELECT funds_available_with_bank,funds_blocked_with_bank,COUNT(*) FROM envelope_batch_status_for_cash GROUP BY funds_available_with_bank,funds_blocked_with_bank');report['funding_states']=[list(x) for x in cur.fetchall()]
with r.pg('example_bank_db','example-bank-postgresql') as c:
 with c.cursor() as cur:
  cur.execute('SELECT payment_status,batching_request_status,COUNT(*) FROM initiate_payment_batch_requests GROUP BY payment_status,batching_request_status');report['example_bank_batches']=[list(x) for x in cur.fetchall()]
  cur.execute('SELECT COUNT(*) FROM initiate_payment_requests');report['example_bank_instructions']=cur.fetchone()[0]
path=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/phase1-evidence/native-payment-state.json');path.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
