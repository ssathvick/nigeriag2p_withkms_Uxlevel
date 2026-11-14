"""Transfer only the authenticated, CEO-approved snapshot into native payment records."""
import hashlib,json,math,uuid
from sqlalchemy import text
from openg2p_bg_task_models.models import BeneficiaryListDetails, DisbursementEnvelope, DisbursementBatch
from openg2p_bg_task_registry_adapters.models import BeneficiaryListSummaryHousehold, BeneficiaryListSummaryFarmer, BeneficiaryListSummaryStudent

def approved_snapshot(pbms, listing):
    row=pbms.execute(text('SELECT p.nsipa_flow,l.nsipa_status,l.nsipa_revision,l.nsipa_payment_hash,l.nsipa_payment_requested_by FROM g2p_beneficiary_list l JOIN g2p_program_definition p ON p.id=l.program_id WHERE l.id=:id'),{'id':listing.id}).mappings().one()
    if not row['nsipa_flow']:return None
    pbms.execute(text('SELECT pg_advisory_xact_lock(73611,:id)'),{'id':listing.id})
    if row['nsipa_status']!='verified' or not row['nsipa_payment_requested_by'] or not row['nsipa_payment_hash']:raise ValueError('CEO-approved payment request is required')
    lines=pbms.execute(text('SELECT beneficiary_id,amount::double precision AS amount,included FROM nsipa_approval_line WHERE list_id=:id ORDER BY id'),{'id':listing.id}).mappings().all()
    digest=hashlib.sha256(json.dumps([(r['beneficiary_id'],r['amount'],r['included']) for r in lines],sort_keys=True).encode()).hexdigest()
    approvals=pbms.execute(text("SELECT stage,approver_id,content_hash FROM nsipa_approval_event WHERE list_id=:id AND revision=:rev AND decision='Approved'"),{'id':listing.id,'rev':row['nsipa_revision']}).mappings().all()
    if digest!=row['nsipa_payment_hash'] or {a['stage'] for a in approvals}!={'Finance','Audit','CEO'} or len({a['approver_id'] for a in approvals})!=3 or any(a['content_hash']!=digest for a in approvals):raise ValueError('Payment snapshot does not match independent final approvals')
    included=[r for r in lines if r['included']]
    if not included or any(not math.isfinite(r['amount']) or not 0<r['amount']<=25000 for r in included):raise ValueError('Invalid approved payment quantities')
    return included

def prepare_snapshot(pbms,bg,listing,program):
    lines=approved_snapshot(pbms,listing)
    if lines is None:return False
    mappings=pbms.execute(text('SELECT benefit_code_id FROM g2p_program_benefit_codes WHERE program_id=:id'),{'id':listing.program_id}).all()
    if len(mappings)!=1:raise ValueError('Exactly one approved digital cash benefit is required')
    benefit=mappings[0][0]
    summary_model={'household':BeneficiaryListSummaryHousehold,'farmer':BeneficiaryListSummaryFarmer,'student':BeneficiaryListSummaryStudent}[program.target_registry.value if hasattr(program.target_registry,'value') else program.target_registry]
    details=bg.query(BeneficiaryListDetails).filter_by(beneficiary_list_id=listing.beneficiary_list_id).all()
    expected=[{'registrant_id':r['beneficiary_id'],'entitlement':{str(benefit):r['amount']},'compute_elements':{str(benefit):{'approval_hash':listing_hash(pbms,listing.id)}}} for r in lines]
    if details:
        actual=[r for d in sorted(details,key=lambda d:d.id) for r in d.registrant_details]
        if sorted(actual,key=lambda r:r['registrant_id'])!=sorted(expected,key=lambda r:r['registrant_id']):raise ValueError('Existing payment records differ from the approved snapshot')
    else:
        for offset in range(0,len(expected),1000):
            chunk=expected[offset:offset+1000]
            bg.add(BeneficiaryListDetails(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-details:'+listing.beneficiary_list_id+':'+str(offset))),beneficiary_list_id=listing.beneficiary_list_id,registrant_details=chunk,number_of_registrants=len(chunk),entitlement_process_status='complete',entitlement_number_of_attempts=0))
    summary=bg.query(summary_model).filter_by(beneficiary_list_id=listing.beneficiary_list_id).first()
    if summary is None:
        total=sum(r['amount'] for r in lines)
        summary=summary_model(id=str(uuid.uuid5(uuid.NAMESPACE_URL,'nsipa-summary:'+listing.beneficiary_list_id)),program_id=listing.program_id,program_mnemonic=program.program_mnemonic,target_registry=program.target_registry.value if hasattr(program.target_registry,'value') else program.target_registry,beneficiary_list_id=listing.beneficiary_list_id,number_of_registrants=len(lines),number_of_entitlements_processed=len(lines),total_disbursement_quantity={str(benefit):total},average_entitlement_per_person={str(benefit):total/len(lines)},entitlement_amount_q1={},entitlement_amount_q2={},entitlement_amount_q3={})
        bg.add(summary)
    bg.commit()
    return True

def listing_hash(pbms,id):
    return pbms.execute(text('SELECT nsipa_payment_hash FROM g2p_beneficiary_list WHERE id=:id'),{'id':id}).scalar_one()
