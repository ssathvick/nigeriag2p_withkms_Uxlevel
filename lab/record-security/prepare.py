from pathlib import Path
import ast,subprocess
root=Path(__file__).parent
main=(root/'original/registry-main.py').read_text()
marker='app = initializer.return_app()'
assert marker in main
main=main.replace(marker,marker+"\nfrom openg2p_registry_core.record_scope import RecordScopeMiddleware\napp.add_middleware(RecordScopeMiddleware)\n",1)
(root/'registry-main.py').write_text(main)
path=root/'original/openg2p_registry_core/controller_services/g2p_awe_proxy_controller_service.py'
s=path.read_text();s='from ..record_scope import persist_decision_scope\n'+s
start=s.index('    async def submit_task_decision(');end=s.index('    async def _validate_change_request_sequence_for_decision',start)
part=s[start:end]
marker='        try:\n            return await AweHelper.get_component().submit_decision('
assert marker in part
part=part.replace(marker,'''        if payload.artifact_type == REGISTRY_INTAKE_FORM_ARTIFACT:
            _, _, expected_request = await self._load_artifact_decision_context(payload.artifact_type, payload.artifact_id)
            page = await AweHelper.get_component().list_tasks_for_request(bearer_token, request_id=expected_request)
            matching = [t for t in page.get('items', []) if str(t.get('id')) == str(payload.task_id) and t.get('stage_order') == payload.current_stage and t.get('status') in ('open', 'claimed')]
            if not matching:
                raise self._invalid_state('The task does not belong to this record and review stage.')
        try:
            result = await AweHelper.get_component().submit_decision(''',1)
needle='''                attachments_ref=payload.attachments_ref,
            )'''
assert needle in part;part=part.replace(needle,needle+'\n            return await persist_decision_scope(payload, result)',1)
s=s[:start]+part+s[end:]
out=root/'g2p_awe_proxy_controller_service.py';out.write_text(s)
for p in [root/'registry-main.py',root/'record_scope.py',out]:ast.parse(p.read_text())
print('Native middleware and decision guards prepared')
controller=(root/'original/openg2p_registry_core/controller_services/intake_form_data_controller_service.py').read_text()
controller='from ..record_scope import actor\n'+controller
controller=controller.replace('requester_sub=requester_sub,',"requester_sub=(actor.get() or {}).get('sub') if (actor.get() or {}).get('ingest') else requester_sub,",1)
(root/'intake_form_data_controller_service.py').write_text(controller)
ast.parse(controller)
helper=(root/'original/awe_helper.py').read_text()
start=helper.index('    async def create_request(');end=helper.index('        async with self._client(token, extra) as client:',start)
helper=helper[:end]+"        if artifact_type.startswith('registry.'):\n            from ..record_scope import sign_registry_request\n            extra.update(sign_registry_request(payload))\n\n"+helper[end:]
ast.parse(helper);(root/'awe_helper.py').write_text(helper)
