from pathlib import Path
from overlay import deploy
root=Path(__file__).parent
p=root/'runtime/intake_form_register_ingest_worker.py';s=p.read_text()
s=s.replace('await _mark_processing(submission_id, session)','claimed = await _mark_processing(submission_id, session)\n                if claimed is None:\n                    return',1)
s=s.replace('submission = await _get_submission(submission_id, session)\n    if submission.register_ingest_process_status', 'submission = (await session.execute(select(G2PIntakeFormSubmission).where(G2PIntakeFormSubmission.submission_id == submission_id).with_for_update())).scalar_one()\n    if submission.register_ingest_process_status in {ProcessStatusEnum.PROCESSED.value, ProcessStatusEnum.PROCESSING.value}:\n        return None\n    if submission.register_ingest_process_status',1)
(root/'patched/intake_form_register_ingest_worker.py').write_text(s)
deploy('register-celery-worker','nsipa-intake-idempotent-worker',{'/usr/local/lib/python3.12/site-packages/openg2p_registry_celery_worker/tasks/intake_form_register_ingest_worker.py':s})
