"""Version-scoped compatibility patches for client-requested review corrections."""
from pathlib import Path
import json,subprocess,hashlib,ast
src=Path(__file__).parent;backup=Path((src/'backup-location.txt').read_text());base='/usr/local/lib/python3.12/site-packages/openg2p_registry_core/';awebase='/usr/local/lib/python3.13/site-packages/awe/'
def read(deploy,path):return subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+deploy,'--','cat',path],text=True)
def mount(deploy,files):
 name='nsipa-client-review-'+('awe' if deploy.endswith('-awe') else 'registry')
 data={f'f{i}':v for i,v in enumerate(files.values())}
 d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy',deploy,'-o','json'],text=True));(backup/(deploy+'.json')).write_text(json.dumps(d))
 cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':name,'namespace':'nigeria'},'data':data}
 s=d['spec']['template']['spec'];container=s['containers'][0];s['volumes']=[v for v in s.get('volumes',[]) if v['name']!=name]+[{'name':name,'configMap':{'name':name}}]
 targets=set(files);container['volumeMounts']=[v for v in container.get('volumeMounts',[]) if v['name']!=name and v['mountPath'] not in targets]+[{'name':name,'mountPath':p,'subPath':f'f{i}','readOnly':True} for i,p in enumerate(files)]
 d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})['nsipa-client-review-hash']=hashlib.sha256(json.dumps(data).encode()).hexdigest()
 for obj in [cm,d]:subprocess.run((['kubectl','apply','--server-side','--field-manager=nsipa-client-review','-f','-'] if obj['kind']=='ConfigMap' else ['kubectl','apply','-f','-']),input=json.dumps(obj),text=True,check=True,stdout=subprocess.DEVNULL)
 for path,text in files.items():
  ast.parse(text);p=src/'patched'/deploy/Path(path).name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 print('Patched',deploy,len(files),'files')

registry={};awe={}
path=base+'services/g2p_register_service.py';old=read('register-staff-portal-api',path);(backup/'g2p_register_service.py').write_text(old)
registry[path]=old.replace('return apply_register_export_sort(query, implementation_class, sort_by)','return apply_register_export_sort(query, implementation_class, sort_by or "-created_at")')
path=base+'services/intake_form_data_service.py';old=read('register-staff-portal-api',path);(backup/'intake_form_data_service.py').write_text(old)
marker='''        _ = finalized_by
        submission = await self._get_submission_or_error(submission_id, session)
        now = datetime.now()'''
replacement='''        _ = finalized_by
        submission = await self._get_submission_or_error(submission_id, session)
        await session.refresh(submission, with_for_update=True)
        if submission.draft_status != IntakeFormStatusEnum.DRAFT.value:
            if submission.approval_status == ApprovalStatusEnum.PENDING.value and submission.awe_request_id:
                return submission
            self._invalid_request("Only a draft or returned submission can be submitted for review.")
        section_payloads = await self._build_section_payloads(submission, session)
        definition = await self._get_register_definition(submission.register_id, session)
        if str(definition.register_mnemonic).lower() == "household" and not str(self._extract_record_name(section_payloads) or "").strip():
            self._invalid_request("Household name is required before submission for review.")
        submission.approval_status = ApprovalStatusEnum.PENDING.value
        now = datetime.now()'''
assert marker in old;new=old.replace(marker,replacement)
new=new.replace('            record_name=record_name,\n            form_id=submission.form_id,','            record_name=record_name,\n            remarks=submission.remarks,\n            form_id=submission.form_id,')
registry[path]=new
path=base+'services/g2p_awe_integration_service.py';old=read('register-staff-portal-api',path);(backup/'g2p_awe_integration_service.py').write_text(old)
needle='idempotency_key=f"intake-{submission.submission_id}",';assert needle in old
registry[path]=old.replace(needle,'idempotency_key=f"intake-{submission.submission_id}-{submission.awe_request_id or \'initial\'}",')
path=base+'schemas/awe_webhook.py';old=read('register-staff-portal-api',path);(backup/'awe_webhook.py').write_text(old);registry[path]=old.replace('    actor: Optional[str] = None','    actor: Optional[str] = None\n    comment: Optional[str] = None')
path=base+'schemas/intake_form.py';old=read('register-staff-portal-api',path);(backup/'intake_form_schema.py').write_text(old);head,tail=old.split('class SubmissionResponsePayload',1);tail=tail.replace('    record_name:', '    remarks: str | None = None\n    record_name:',1);registry[path]=head+'class SubmissionResponsePayload'+tail
path=base+'services/g2p_awe_webhook_service.py';old=read('register-staff-portal-api',path);(backup/'g2p_awe_webhook_service.py').write_text(old)
registry[path]=old.replace('submission.remarks = "Rejected via AWE approval workflow"','submission.remarks = (event.comment or "No correction details were supplied. Contact the reviewer before resubmitting.")[:2000]\n            submission.draft_status = "DRAFT"').replace('change_request.remarks = "Rejected via AWE approval workflow"','change_request.remarks = (event.comment or "No correction details were supplied. Contact the reviewer.")[:2000]')
path=awebase+'schemas/callback.py';old=read('commons-services-awe',path);(backup/'awe_callback.py').write_text(old);awe[path]=old.replace('    actor: Optional[str] = None','    actor: Optional[str] = None\n    comment: Optional[str] = None')
path=awebase+'services/webhook.py';old=read('commons-services-awe',path);(backup/'awe_webhook_service.py').write_text(old);awe[path]=old.replace('        actor=event_payload.get("actor"),','        actor=event_payload.get("actor"),\n        comment=event_payload.get("comment"),')
path=awebase+'services/engine.py';old=read('commons-services-awe',path);(backup/'awe_engine.py').write_text(old)
needle='        await emit_event(session, request, "request_rejected", {"actor": actor})';assert needle in old
awe[path]=old.replace(needle,'''        rejected_decisions = [d for d in await _stage_decisions(session, request.id, task.stage_order) if d.action == "reject"]
        latest_rejection = max(rejected_decisions, key=lambda d: d.created_at) if rejected_decisions else None
        await emit_event(session, request, "request_rejected", {"actor": actor, "comment": latest_rejection.comment if latest_rejection else None})''',1)
for code in [*registry.values(),*awe.values()]:ast.parse(code)
mount('register-staff-portal-api',registry);mount('commons-services-awe',awe)
