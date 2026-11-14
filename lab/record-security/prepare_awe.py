from pathlib import Path
import ast
root=Path(__file__).parent
s=(root/'original/awe/main.py').read_text()
marker='app = FastAPI('
start=s.index(marker);end=s.index('\n)',start)+2
s=s[:end]+"\nfrom .record_scope import ScopeMiddleware\napp.add_middleware(ScopeMiddleware)\n"+s[end:]
(root/'awe-main.py').write_text(s)
s=(root/'original/awe/services/auth.py').read_text()
s=s.replace('    return CallerIdentity(',"    from ..record_scope import verified_identity\n    verified_identity(claims)\n    return CallerIdentity(",1)
(root/'awe-auth.py').write_text(s)
s=(root/'original/awe/controllers/task.py').read_text()
s=s.replace('from ..db import get_db','from ..record_scope import can_review_registry\nfrom ..db import get_db',1)
start=s.index('async def decide(');end=s.index('    if request.status not in',start)
s=s[:end]+'''    if not await can_review_registry(session, request, task):
        return error(403, "AWE-008", "This record is not awaiting your Registry review level.")

'''+s[end:]
(root/'awe-task.py').write_text(s)
s=(root/'original/awe/controllers/request.py').read_text()
s=s.replace('from fastapi import ', 'from fastapi import Request, ',1)
s=s.replace('from ..db import get_db','from ..record_scope import can_create_registry\nfrom sqlalchemy import text\nfrom ..db import get_db',1)
s=s.replace('async def create_request(\n    payload: CreateRequestIn,','async def create_request(\n    payload: CreateRequestIn,\n    http_request: Request,',1)
marker='    if idempotency_key:\n'
check='''    if not await can_create_registry(payload, identity, http_request):
        return error(403, "AWE-008", "This record is not an editable submission owned by your field account.")
'''
s=s.replace(marker,check+marker,1)
marker='''        if existing is not None:
            return existing.response_payload'''
replacement='''        if existing is not None:
            cached_id = (existing.response_payload or {}).get('request_id')
            cached_request = await session.get(ApprovalRequest, cached_id) if cached_id else None
            if cached_request and cached_request.artifact_type.startswith('registry.'):
                if str(cached_request.artifact_id) != str(payload.artifact_id) or not await can_create_registry(payload, identity, http_request):
                    return error(403, "AWE-008", "The idempotency key belongs to another record.")
            return existing.response_payload'''
assert marker in s;s=s.replace(marker,replacement,1)
(root/'awe-request.py').write_text(s)
for name in ['awe-main.py','awe-auth.py','awe-task.py','awe-request.py','awe_scope.py']:ast.parse((root/name).read_text())
print('AWE read scope and decision guard prepared')
