import os,pathlib,json,subprocess
r=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react');f=json.loads((r/'evidence/connected-payments/fixture.json').read_text())
code='''import logging,json
from openg2p_bg_task_celery_workers.app import Initializer
Initializer()
logging.disable(logging.CRITICAL)
from openg2p_bg_task_celery_workers.app import get_engine
from sqlalchemy.orm import sessionmaker
from openg2p_pbms_models.models import G2PBeneficiaryList,G2PProgramDefinition
from openg2p_bg_task_celery_workers.tasks.nsipa_payment_snapshot import prepare_snapshot
from openg2p_bg_task_models.models import BeneficiaryListDetails,DisbursementBatch,DisbursementEnvelope
from openg2p_bg_task_celery_workers.tasks.disbursement_envelope_creation_worker import disbursement_envelope_creation_worker
from openg2p_bg_task_celery_workers.tasks.disbursement_batch_creation_worker import disbursement_batch_creation_worker
disbursement_envelope_creation_worker.run(LIST_ID)
disbursement_batch_creation_worker.run(LIST_ID)
eng=get_engine()
with sessionmaker(bind=eng['db_engine_pbms'])() as p, sessionmaker(bind=eng['db_engine_bg_task'])() as b:
 l=p.query(G2PBeneficiaryList).filter_by(id=LIST_ID).one();program=p.query(G2PProgramDefinition).filter_by(id=l.program_id).one()
 assert prepare_snapshot(p,b,l,program)
 assert prepare_snapshot(p,b,l,program)
 details=b.query(BeneficiaryListDetails).filter_by(beneficiary_list_id=l.beneficiary_list_id).all()
 entries=[r for d in details for r in d.registrant_details]
 assert len(entries)==1 and entries[0]['registrant_id']==EXPECTED_ID
 assert list(entries[0]['entitlement'].values())==[1.0]
 batches=b.query(DisbursementBatch).filter_by(beneficiary_list_id=l.beneficiary_list_id).all()
 envelopes=b.query(DisbursementEnvelope).filter_by(beneficiary_list_id=l.beneficiary_list_id).all()
 print('RESULT:'+json.dumps({'snapshot_count':len(entries),'corrected_ngn':1.0,'excluded_beneficiary_omitted':True,'snapshot_retry_idempotent':True,'batch_count':len(batches),'envelope_count':len(envelopes)}))
'''.replace('LIST_ID',str(f['list_id'])).replace('EXPECTED_ID',repr(f['expected_beneficiary']))
p=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/pbms-celery-worker','--','python','-'],input=code,capture_output=True,text=True)
if p.returncode:
 print(p.stderr[-2500:]);raise SystemExit(1)
result=next(line[7:] for line in p.stdout.splitlines() if line.startswith('RESULT:'))
(r/'evidence/connected-payments/snapshot-results.json').write_text(result);print(result)
