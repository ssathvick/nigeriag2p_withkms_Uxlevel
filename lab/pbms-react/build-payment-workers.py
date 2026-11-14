from pathlib import Path
r=Path(__file__).parent
p=r/'backend-reference/openg2p_bg_task_celery_workers__tasks__disbursement_envelope_creation_worker.py';s=p.read_text()
s=s.replace('import logging','from .nsipa_payment_snapshot import prepare_snapshot\nimport logging',1)
needle='            disbursement_cycle: G2PDisbursementCycle = ('
s=s.replace(needle,"            nsipa_payment = prepare_snapshot(pbms_session,bg_task_session,beneficiary_list,program_definition)\n            if nsipa_payment and bg_task_session.query(DisbursementEnvelope).filter_by(beneficiary_list_id=beneficiary_list.beneficiary_list_id).count():\n                beneficiary_list.envelope_creation_status='complete'\n                if beneficiary_list.disbursement_batch_creation_status=='not_applicable': beneficiary_list.disbursement_batch_creation_status='pending'\n                pbms_session.commit()\n                return\n\n"+needle)
s=s.replace('            # Use the helper class for envelope creation',"            if nsipa_payment:\n                for payload in disbursement_envelope_request_message:\n                    payload.id=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-envelope:'+beneficiary_list.beneficiary_list_id+':'+str(payload.benefit_code_id)))\n            # Use the helper class for envelope creation")
s=s.replace("                    payload.id=str(uuid.uuid5","                    payload.disbursement_schedule_date=disbursement_cycle.disbursement_schedule_date\n                    payload.id=str(uuid.uuid5")
s=s.replace("            pbms_session.commit()\n            bg_task_session.commit()","            if nsipa_payment:\n                bg_task_session.commit()\n                pbms_session.commit()\n            else:\n                pbms_session.commit()\n                bg_task_session.commit()")
(r/'nsipa_disbursement_envelope_worker.py').write_text(s)
p=r/'backend-reference/openg2p_bg_task_celery_workers__tasks__disbursement_batch_creation_worker.py';s=p.read_text().replace('import logging','from .nsipa_payment_snapshot import approved_snapshot\nimport logging',1)
needle='            beneficiary_list_details = ('
s=s.replace(needle,"            nsipa_lines=approved_snapshot(pbms_session,beneficiary_list)\n            if nsipa_lines is not None and bg_task_session.query(DisbursementBatch).filter_by(beneficiary_list_id=beneficiary_list.beneficiary_list_id).count():\n                beneficiary_list.disbursement_batch_creation_status='complete'\n                pbms_session.commit()\n                return\n"+needle)
(r/'nsipa_disbursement_batch_worker.py').write_text(s)
