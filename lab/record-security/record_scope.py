"""Native Registry record isolation. IAM validates JWTs before this middleware.

Every scoped SQLAlchemy transaction changes to a non-owner, NOBYPASSRLS role.
SET LOCAL and a ContextVar prevent pooled-connection and concurrent-user leakage.
Workers/webhooks retain native service authority; browser payloads cannot choose it.
"""
from contextvars import ContextVar
import os
from sqlalchemy import event, text
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

actor = ContextVar('nsipa_registry_actor', default=None)
ROLES = {'Registry Field Agent':'field', 'Registry First Reviewer':'level1',
         'Registry Second Reviewer':'level2', 'Registry Officer':'officer',
         'Registry Administrator':'admin'}

def sign_registry_request(payload):
    import hmac,hashlib,json,time
    key=os.environ.get('NSIPA_REGISTRY_REQUEST_KEY')
    if not key:raise RuntimeError('Registry request signing key is unavailable')
    stamp=str(int(time.time()))
    body={k:payload.get(k) for k in ['artifact_type','artifact_id','policy_key','requester','context','callback_url','callback_secret_id']}
    message=stamp+'\n'+json.dumps(body,sort_keys=True,separators=(',',':'))
    return {'X-NSIPA-Registry-Timestamp':stamp,'X-NSIPA-Registry-Signature':hmac.new(key.encode(),message.encode(),hashlib.sha256).hexdigest()}

@event.listens_for(Session, 'after_begin')
def enforce_transaction_scope(session, transaction, connection):
    current=actor.get()
    if current is None:return  # Native worker / authenticated server callback.
    for key,value in [('role',current['role']),('sub',current.get('sub','')),('name',current.get('name',''))]:
        connection.execute(text("SELECT set_config(:key,:value,true)"),{'key':'nsipa.'+key,'value':value})
    if current['role']!='admin':connection.exec_driver_sql('SET LOCAL ROLE nsipa_registry_scoped')

class NoRecordCache:
    def __init__(self, backend):self.backend=backend
    async def get_with_ttl(self,key):return 0,None
    async def get(self,key):return None
    async def set(self,*args,**kwargs):return None
    def __getattr__(self,name):return getattr(self.backend,name)

# A shared pre-security response cache must never bypass RLS or retain a handed-off record.
from fastapi_cache import FastAPICache
_backend=FastAPICache.get_backend.__func__
FastAPICache.get_backend=classmethod(lambda cls: NoRecordCache(_backend(cls)) if actor.get() is not None else _backend(cls))

class RecordScopeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self,request,call_next):
        if request.url.path=='/awe/webhooks/decision':
            # The native controller validates this signed server callback itself.
            return await call_next(request)
        principal=getattr(request.state,'auth',None)
        roles=set((getattr(principal,'client_roles',None) or {}).get('register-staff-portal',[]))
        scopes={ROLES[r] for r in roles if r in ROLES}
        if len(scopes)>1:
            return JSONResponse({'error':'Use one dedicated Registry persona per account.'},403)
        scope=next(iter(scopes),'denied')
        current={'role':scope,'sub':str(getattr(principal,'sub','') or ''),
                 'name':str(getattr(principal,'name','') or '')}
        owner=request.headers.get('X-NSIPA-Field-Owner')
        integration=bool(os.environ.get('NSIPA_ODK_SERVICE_SUB')) and current['sub']==os.environ.get('NSIPA_ODK_SERVICE_SUB') and 'Intake Officer' in roles
        if owner:
            if not integration:return JSONResponse({'error':'Field ownership cannot be selected by this account.'},403)
            from openg2p_fastapi_common.context import get_async_session_maker
            async with get_async_session_maker()() as session:
                name=(await session.execute(text('SELECT nsipa_ingest_owner(:sub)'),{'sub':owner})).scalar()
            if not name:return JSONResponse({'error':'Unrecognized field capture owner.'},403)
            current={'role':'field','sub':owner,'name':name,'ingest':True};scope='field'
        elif integration and request.url.path.startswith(('/intake-form-data/','/register-data/','/awe/')):
            return JSONResponse({'error':'Authenticated offline capture owner is required.'},403)
        token=actor.set(current)
        try:
            if scope not in ('admin','field') and request.url.path.startswith('/intake-form-data/'):
                if any(word in request.url.path for word in ['save_','finalize_','delete_','approve_','reject_']):
                    return JSONResponse({'error':'This Registry persona cannot capture or change submissions.'},403)
            # Approval must use assigned native AWE tasks, never the legacy direct action.
            if request.url.path.endswith(('/approve_intake_form_submission','/reject_intake_form_submission')):
                return JSONResponse({'error':'Use the assigned independent review task.'},403)
            response=await call_next(request)
            response.headers['Cache-Control']='no-store, private'
            response.headers['Vary']='Cookie, Authorization'
            response.headers['X-Registry-Record-Scope']=scope
            return response
        finally:actor.reset(token)

async def persist_decision_scope(payload, result):
    """Called only after AWE validates and saves the authenticated assigned decision."""
    current=actor.get()
    if not current or payload.artifact_type!='registry.intake_form':return result
    from openg2p_fastapi_common.context import get_async_session_maker
    async with get_async_session_maker()() as session:
        await session.execute(text('SELECT nsipa_security_decision(:id,:stage,:action)'),
             {'id':str(payload.artifact_id),'stage':int(payload.current_stage),'action':payload.action})
        await session.commit()
    return result
