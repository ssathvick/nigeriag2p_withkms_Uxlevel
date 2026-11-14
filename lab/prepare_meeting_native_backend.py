"""Prepare reviewable, version-scoped changes to the existing Registry/AWE services."""
import ast,json
from pathlib import Path
ROOT=Path(__file__).parent/'meeting-native';manifest=json.loads((ROOT/'manifest.json').read_text());changes={}
def edit(deploy,suffix,fn):
 source=next(k for k,v in manifest[deploy].items() if v.endswith(suffix));original=(ROOT/source).read_text();changed=fn(original)
 if changed==original:return
 ast.parse(changed);p=ROOT/source.replace('original/','patched/');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(changed);changes.setdefault(deploy,{})[p.relative_to(ROOT).as_posix()]=manifest[deploy][source]
D='commons-services-awe';R='register-staff-portal-api'
edit(D,'awe/schemas/request.py',lambda s:s.replace('VALID_DECISION_ACTIONS = {"approve", "reject", "abstain"}','VALID_DECISION_ACTIONS = {"approve", "reject", "return", "abstain"}'))
def engine(s):
 marker='    policy = await _load_policy(session, request.policy_id)\n    stage = _stage_at(policy, task.stage_order)'
 addition='''    if action == "return":
        await _close_stage_open_tasks(session, request.id, task.stage_order)
        request.status = "returned"
        request.completed_at = utcnow()
        decisions = await _stage_decisions(session, request.id, task.stage_order)
        latest = max((d for d in decisions if d.action == "return"), key=lambda d: d.created_at, default=None)
        await emit_event(session, request, "request_returned", {"actor": actor, "comment": latest.comment if latest else None})
        return request

'''
 addition='''    decision = await session.get(ApprovalDecision, task.decision_id) if task.decision_id else None
    await emit_event(session, request, "decision_" + action, {"actor": actor, "comment": decision.comment if decision else None})

'''+addition
 assert marker in s;return s.replace(marker,addition+marker,1).replace('_TERMINAL = {"request_approved", "request_rejected", "request_cancelled"}','_TERMINAL = {"request_approved", "request_rejected", "request_cancelled", "request_returned"}').replace('_DELIVERABLE = _TERMINAL | {','_DELIVERABLE = _TERMINAL | {\n    "decision_approve", "decision_reject", "decision_return",')
edit(D,'awe/services/engine.py',engine)
def task(s):
 s=s.replace('from ..models import ApprovalDecision, ApprovalRequest, ApprovalTask','from ..models import ApprovalDecision, ApprovalRequest, ApprovalTask, ApprovalPolicy')
 start=s.index('async def decide(');a=s[:start];b=s[start:]
 b=b.replace('    task = await session.get(ApprovalTask, task_id)','    task = (await session.execute(select(ApprovalTask).where(ApprovalTask.id == task_id).with_for_update())).scalar_one_or_none()',1)
 marker='    decision_actor = identity.name or identity.subject'
 checks='''    if request.status not in ("pending", "in_review"):
        return error(409, "AWE-007", "This review is closed")
    if payload.action in ("reject", "return") and not (payload.comment or "").strip():
        return error(422, "AWE-007", "A reason is required for rejection or return for correction")
    if payload.action == "return" and not request.artifact_type.startswith("registry."):
        return error(422, "AWE-007", "Return for correction is supported for registry records")
    policy = await session.get(ApprovalPolicy, request.policy_id)
    identities = {identity.subject, identity.assignee_id, identity.name}
    if policy and policy.forbid_self_approval and request.requester in identities:
        return error(403, "AWE-008", "You cannot review your own submission")
    if policy and policy.forbid_repeat_approvers:
        previous = (await session.execute(select(ApprovalDecision.actor).where(ApprovalDecision.request_id == request.id, ApprovalDecision.stage_order < task.stage_order))).scalars().all()
        if identities.intersection(previous):
            return error(403, "AWE-008", "A different reviewer must complete this stage")
'''
 assert marker in b;b=b.replace(marker,checks+'\n'+marker,1);s=a+b
 s=s.replace('    if status_filter:\n        task_filters.append(ApprovalTask.status == status_filter)','''    if status_filter == "pending":
        task_filters.append(ApprovalTask.status.in_(("open", "claimed")))
    elif status_filter in ("rejected", "returned"):
        action = "reject" if status_filter == "rejected" else "return"
        task_filters.append(ApprovalTask.decision_id.in_(select(ApprovalDecision.id).where(ApprovalDecision.action == action)))
    elif status_filter:
        task_filters.append(ApprovalTask.status == status_filter)''')
 return s
edit(D,'awe/controllers/task.py',task)
edit(R,'helpers/awe_helper.py',lambda s:s.replace('{"approve", "reject", "abstain"}','{"approve", "reject", "return", "abstain"}').replace('            assignee="me",\n            request_id=request_id,','            assignee="*" if request_id else "me",\n            request_id=request_id,',1).replace('            and task.get("status") == "completed"\n            and task.get("decision_action") == "approve"',''))
def webhook(s):
 s='from sqlalchemy import text\n'+s if not s.startswith('from __future__') else s.replace('from __future__ import annotations','from __future__ import annotations\nfrom sqlalchemy import text',1)
 s=s.replace('{"request_approved", "request_rejected", "request_cancelled"}','{"request_approved", "request_rejected", "request_cancelled", "request_returned"}')
 s=s.replace('            submission.draft_status = "DRAFT"','            submission.draft_status = "FINAL"')
 marker='        await session.flush()\n        return log_row'
 s=s.replace(marker,'''        await session.flush()
        if event.comment:
            await session.execute(text("INSERT INTO g2p_registry_review_comments(event_id,comment) VALUES(:event,:comment) ON CONFLICT(event_id) DO UPDATE SET comment=EXCLUDED.comment"), {"event":event.event_id,"comment":event.comment})
        return log_row''',1)
 marker='        if event.event_type == "request_rejected":'
 # A returned attempt is closed in AWE; the same native intake becomes editable.
 start=s.index('    async def _apply_terminal_event_for_intake_form_submission')
 a,b=s[:start],s[start:]
 b=b.replace(marker,'''        if event.event_type == "request_returned":
            await session.execute(text("INSERT INTO g2p_registry_return_history(event_id,artifact_id,artifact_type,request_id,actor,reason,payload) SELECT :event,:artifact,:type,:request,:actor,:reason,jsonb_agg(to_jsonb(h)) FROM g2p_intake_form_households h WHERE CAST(h.submission_id AS text)=:artifact ON CONFLICT DO NOTHING"), {"event":event.event_id,"artifact":event.artifact_id,"type":event.artifact_type,"request":event.request_id,"actor":event.actor,"reason":event.comment})
            submission.approval_status = ApprovalStatusEnum.PENDING.value
            submission.draft_status = "DRAFT"
            submission.remarks = (event.comment or "Correction requested")[:2000]
            submission.approved_by = event.actor
            submission.approved_at = datetime.now()
            return

'''+marker,1)
 a=a.replace(marker,'''        if event.event_type == "request_returned":
            await session.execute(text("INSERT INTO g2p_registry_return_history(event_id,artifact_id,artifact_type,request_id,actor,reason,payload) SELECT :event,:artifact,:type,:request,:actor,:reason,to_jsonb(p) FROM g2p_register_change_request_payloads p WHERE p.change_request_id=:artifact ON CONFLICT DO NOTHING"), {"event":event.event_id,"artifact":event.artifact_id,"type":event.artifact_type,"request":event.request_id,"actor":event.actor,"reason":event.comment})
            change_request.remarks = (event.comment or "Correction requested")[:2000]
            change_request.approval_status = ApprovalStatusEnum.PENDING.value
            change_request.awe_request_status_summary = "returned-stage" + str(event.stage_order or 1)
            return

'''+marker,1)
 return a+b
edit(R,'services/g2p_awe_webhook_service.py',webhook)
edit(R,'helpers/awe_status_summary.py',lambda s:s.replace('    "cancelled": 2,','    "cancelled": 2,\n    "returned": 2,'))
def reconcile(s):
 marker='    rows = ('
 add='''    model = G2PRegisterChangeRequest if artifact_type == REGISTRY_CHANGE_REQUEST_ARTIFACT else G2PIntakeFormSubmission
    key = model.change_request_id if artifact_type == REGISTRY_CHANGE_REQUEST_ARTIFACT else model.submission_id
    current_request = select(model.awe_request_id).where(key == artifact_id).scalar_subquery()
'''
 assert marker in s;s=s.replace(marker,add+marker,1)
 s=s.replace('                G2PAweReqEvent.artifact_id == artifact_id,','                G2PAweReqEvent.artifact_id == artifact_id,\n                G2PAweReqEvent.request_id == current_request,',1)
 return s
edit(R,'services/g2p_awe_status_reconcile.py',reconcile)
def intake(s):
 s=s.replace('submission_source=ChangeRequestSourceEnum.STAFF_PORTAL.value,','submission_source="ODK_COLLECT" if created_by == "NSIPA ODK Synchronization" else ChangeRequestSourceEnum.STAFF_PORTAL.value,',1)
 marker='        submission.approval_status = ApprovalStatusEnum.PENDING.value\n        now = datetime.now()'
 addition='''        if str(definition.register_mnemonic).lower() == "household":
            rows = [r for section in section_payloads for r in (section.records or []) if isinstance(r, dict)]
            household = next((r for r in rows if r.get("household_head_name")), {})
            if submission.first_created_at >= datetime(2026, 11, 12, 16, 45):
                if household.get("consent_status") != "YES" or any(not str(household.get(k) or "").strip() for k in ("sponsor_name", "respondent_name")):
                    self._invalid_request("Record the sponsor, informed consent and respondent before submitting.")
            for section in section_payloads:
                if section.section_id == "hh_members":
                    for member in section.records or []:
                        if not member.get("birth_date") and member.get("estimated_age") is None:
                            self._invalid_request("Each household member needs either age or date of birth.")
                        age = member.get("estimated_age")
                        if age is not None and not 0 <= int(age) <= 120:
                            self._invalid_request("Member age must be between 0 and 120.")
'''
 assert marker in s;s=s.replace(marker,addition+marker,1)
 # Workflow filters apply to native submission headers before pagination.
 marker='            intake_class = await self._resolve_intake_form_class(register_id, session)\n            match_subquery'
 add='''            workflow_status = None
            if isinstance(filter_by, str):
                import json
                filter_by = json.loads(filter_by) if filter_by else {}
            if isinstance(filter_by, dict):
                filter_by = dict(filter_by)
                workflow_status = filter_by.pop("workflow_status", None)
'''
 assert marker in s;s=s.replace(marker,add+marker,1)
 marker='            base_filters = [G2PIntakeFormSubmission.register_id == register_id]'
 add='''
            header = G2PIntakeFormSubmission
            if workflow_status == "draft":
                base_filters.append(header.draft_status == "DRAFT")
            elif workflow_status == "pending":
                base_filters.extend([header.draft_status == "FINAL", header.approval_status == "PENDING"])
            elif workflow_status == "returned":
                base_filters.extend([header.draft_status == "DRAFT", header.awe_request_status_summary.like("returned%")])
            elif workflow_status in ("approved", "rejected"):
                base_filters.append(header.approval_status == workflow_status.upper())
'''
 s=s.replace(marker,marker+add,1)
 # Keep reference matching inside the existing data-policy constrained subquery.
 s=s.replace('conditions.append(intake_class.search_text.ilike(f"%{search_text}%"))','conditions.append(or_(intake_class.search_text.ilike(f"%{search_text}%"), intake_class.application_reference.ilike(f"%{search_text}%")))',1)
 return s
edit(R,'services/intake_form_data_service.py',intake)
def change_search(s):
 marker='        search_conditions = [G2PRegisterChangeRequestPayload.search_text.ilike(search_query)]'
 add='''
        if isinstance(filter_by, str):
            import json
            filter_by = json.loads(filter_by) if filter_by else {}
        workflow_status = (filter_by or {}).get("workflow_status")
        if workflow_status in ("pending", "approved", "rejected"):
            search_conditions.append(G2PRegisterChangeRequest.approval_status == workflow_status.upper())
        if workflow_status == "pending":
            search_conditions.append(~G2PRegisterChangeRequest.awe_request_status_summary.like("returned%"))
        elif workflow_status == "returned":
            search_conditions.append(G2PRegisterChangeRequest.awe_request_status_summary.like("returned%"))
'''
 assert marker in s;s=s.replace(marker,marker+add,1)
 # Reuse the same native change request after correction; keep the previous attempt snapshot.
 s=s.replace('G2PRegisterChangeRequest.approval_status == ApprovalStatusEnum.PENDING.value,\n                )','G2PRegisterChangeRequest.approval_status == ApprovalStatusEnum.PENDING.value,\n                    or_(G2PRegisterChangeRequest.awe_request_status_summary.is_(None), ~G2PRegisterChangeRequest.awe_request_status_summary.like("returned%")),\n                )',1)
 marker='            session.add(g2p_register_change_request)'
 addition='''            returned = (await session.execute(select(G2PRegisterChangeRequest).where(
                G2PRegisterChangeRequest.internal_record_id == change_request_request_payload.internal_record_id,
                G2PRegisterChangeRequest.section_id == change_request_request_payload.section_id,
                G2PRegisterChangeRequest.approval_status == ApprovalStatusEnum.PENDING.value,
                G2PRegisterChangeRequest.awe_request_status_summary.like("returned%")
            ).with_for_update())).scalars().first()
            if returned:
                previous_payload = await self._get_change_request_payload(returned.change_request_id, session)
                previous_payload.change_payload = g2p_register_change_request._payload.change_payload
                previous_payload.search_text = g2p_register_change_request._payload.search_text
                returned.record_name = g2p_register_change_request.record_name
                returned.awe_request_status_summary = "pending-stage1"
                g2p_register_change_request = returned
'''
 s=s.replace(marker,addition+marker,1)
 return s
edit(R,'services/g2p_register_change_request_service.py',change_search)
edit(R,'services/g2p_awe_integration_service.py',lambda s:s.replace('idempotency_key=f"cr-{change_request.change_request_id}",','idempotency_key=f"cr-{change_request.change_request_id}-{change_request.awe_request_id or \'initial\'}",'))
metadata_fields=['sponsor_name','consent_status','respondent_name','enumerator_name','survey_community','health_insurance_status','income_source']
def household_model(s):
 fields='\n'.join('    '+f+': Mapped[str] = mapped_column(String, nullable=True)' for f in metadata_fields)
 fields+='\n    monthly_household_income: Mapped[float] = mapped_column(Numeric, nullable=True)'
 return s.replace('class G2PHousehold:\n','class G2PHousehold:\n\n'+fields+'\n',1)
def household_schema(s):
 fields='\n'.join('    '+f+': Optional[str] = None' for f in metadata_fields)
 fields+='\n    monthly_household_income: Optional[float] = None'
 s=s.replace('class G2PSchemaHousehold:\n','class G2PSchemaHousehold:\n\n'+fields+'\n',1)
 s=s.replace('    husband_dead: Optional[bool] = None',fields+'\n\n    husband_dead: Optional[bool] = None')
 return s
edit(R,'register_domain/models/household.py',household_model)
edit(R,'register_domain/schemas/household.py',household_schema)
# Expose all native review attempts in the existing detail responses.
edit(R,'schemas/intake_form.py',lambda s:s.replace('class SubmissionResponsePayload(IntakeFormData):','class SubmissionResponsePayload(IntakeFormData):\n    review_history: list[dict] = []',1))
edit(R,'schemas/change_request.py',lambda s:s.replace('class ChangeRequestData(BaseModel):','class ChangeRequestData(BaseModel):\n    review_history: list[dict] = []',1))
def detail_history(s):
 s='from .workflow_review_history import review_history\n'+s
 marker='            return self._build_submission_response_payload(\n                submission,\n                sections,\n                self._extract_record_name(sections),\n            )'
 assert marker in s;s=s.replace(marker,'''            response = self._build_submission_response_payload(submission, sections, self._extract_record_name(sections))
            response.review_history = await review_history(session, str(submission_id))
            return response''',1)
 return s
edit(R,'services/intake_form_data_service.py',lambda s:s) # retain generated filtering changes
p=ROOT/'patched/register-staff-portal-api/openg2p_registry_core/services/intake_form_data_service.py';p.write_text(detail_history(p.read_text()))
p=ROOT/'patched/register-staff-portal-api/openg2p_registry_core/services/g2p_register_change_request_service.py';s=p.read_text();s='from .workflow_review_history import review_history\n'+s;s=s.replace('            await session.commit()\n            return change_request_data','            change_request_data.review_history = await review_history(session, change_request_id)\n            await session.commit()\n            return change_request_data',1);p.write_text(s)
helper='''from sqlalchemy import text
async def review_history(session, artifact_id):
    result = await session.execute(text("SELECT e.event_type,e.actor,e.occurred_at::text AS occurred_at,e.request_id,e.status,e.stage_order,COALESCE(c.comment,h.reason) AS reason FROM awe_req_events e LEFT JOIN g2p_registry_return_history h ON h.event_id=e.event_id LEFT JOIN g2p_registry_review_comments c ON c.event_id=e.event_id WHERE e.artifact_id=:id AND e.applied=true AND (e.event_type IN ('stage_started','stage_completed','request_approved','request_rejected','request_returned','request_cancelled') OR e.event_type LIKE 'decision_%') ORDER BY e.occurred_at,e.received_at"), {"id":artifact_id})
    events = [dict(row._mapping) for row in result]
    exists = (await session.execute(text("SELECT to_regclass('public.g2p_mbr_source_archive')"))).scalar()
    if exists:
        old = await session.execute(text("SELECT 'decision_' || (d.body->>'action') AS event_type,d.body->>'actor' AS actor,d.body->>'created_at' AS occurred_at,d.body->>'request_id' AS request_id,d.body->>'action' AS status,(d.body->>'stage_order')::integer AS stage_order,d.body->>'comment' AS reason FROM g2p_mbr_source_archive d JOIN g2p_mbr_source_archive r ON r.source_db='awe' AND r.source_table='approval_request' AND r.body->>'id'=d.body->>'request_id' WHERE d.source_db='awe' AND d.source_table='approval_decision' AND r.body->>'artifact_id'=:id"), {"id":artifact_id})
        events += [dict(row._mapping) for row in old]
    return sorted(events, key=lambda e:e.get('occurred_at') or '')
'''
p=ROOT/'patched/register-staff-portal-api/openg2p_registry_core/services/workflow_review_history.py';p.write_text(helper);changes[R][p.relative_to(ROOT).as_posix()]='/usr/local/lib/python3.12/site-packages/openg2p_registry_core/services/workflow_review_history.py'
(ROOT/'changes.json').write_text(json.dumps(changes,indent=2));print({k:len(v) for k,v in changes.items()})
