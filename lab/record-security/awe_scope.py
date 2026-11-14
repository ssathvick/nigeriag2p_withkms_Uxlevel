"""Scope AWE read APIs after native JWT verification; preserve non-Registry workflows."""
from contextvars import ContextVar
from sqlalchemy import event,text
from sqlalchemy.orm import Session

current=ContextVar('nsipa_awe_identity',default=None)
method=ContextVar('nsipa_awe_method',default=None)
ROLES={'Registry Field Agent':'field','Registry First Reviewer':'level1','Registry Second Reviewer':'level2','Registry Officer':'officer','Registry Administrator':'admin'}
def verified_identity(claims):
    roles=set(((claims.get('resource_access') or {}).get('register-staff-portal') or {}).get('roles') or [])
    scopes={ROLES[r] for r in roles if r in ROLES}
    current.set({'role':next(iter(scopes)) if len(scopes)==1 else 'denied','sub':claims.get('sub','')})

@event.listens_for(Session,'after_begin')
def set_scope(session,transaction,connection):
    who=current.get()
    if who is None:return
    connection.execute(text("SELECT set_config('nsipa.role',:role,true),set_config('nsipa.sub',:sub,true)"),who)
    if method.get()=='GET' and who['role']!='admin':connection.exec_driver_sql('SET LOCAL ROLE nsipa_awe_scoped')

class ScopeMiddleware:
    def __init__(self,app):self.app=app
    async def __call__(self,scope,receive,send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        who=current.set({'role':'denied','sub':''});verb=method.set(scope['method'])
        try:await self.app(scope,receive,send)
        finally:current.reset(who);method.reset(verb)

async def can_review_registry(session,request,task):
    if not request.artifact_type.startswith('registry.'):return True
    who=current.get() or {};expected={'level1':1,'level2':2}.get(who.get('role'))
    if expected!=task.stage_order:return False
    return bool((await session.execute(text('SELECT nsipa_awe_visible_request(:id)'),{'id':str(request.id)})).scalar())

async def can_create_registry(payload,identity,http_request):
    if not payload.artifact_type.startswith('registry.'):return True
    who=current.get() or {}
    import os
    import hmac,hashlib,json,time
    key=os.environ.get('NSIPA_REGISTRY_REQUEST_KEY','');stamp=http_request.headers.get('X-NSIPA-Registry-Timestamp','')
    try:
        if not key or abs(time.time()-int(stamp))>60:return False
    except ValueError:return False
    body={k:getattr(payload,k,None) for k in ['artifact_type','artifact_id','policy_key','requester','context','callback_url','callback_secret_id']}
    message=stamp+'\n'+json.dumps(body,sort_keys=True,separators=(',',':'))
    expected=hmac.new(key.encode(),message.encode(),hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,http_request.headers.get('X-NSIPA-Registry-Signature','')):return False
    integration=bool(os.environ.get('NSIPA_ODK_SERVICE_SUB')) and identity.subject==os.environ.get('NSIPA_ODK_SERVICE_SUB') and identity.raw_claims.get('azp')=='nsipa-odk-registry-sync'
    if payload.artifact_type!='registry.intake_form':return False
    if not integration and (who.get('role')!='field' or payload.requester!=identity.subject):return False
    # Validate authoritative ownership before an AWE request or idempotency response is exposed.
    import httpx,uuid,datetime
    csrf=str(uuid.uuid4())
    body={'request_header':{'sender_app_mnemonic':'NSIPA record security','sender_app_url':'http://commons-services-awe','request_id':str(uuid.uuid4()),'request_timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat()},'request_body':{'request_payload':{'submission_id':payload.artifact_id}}}
    async with httpx.AsyncClient(timeout=20) as client:
        headers={'Authorization':http_request.headers.get('authorization',''),'X-CSRF-Token':csrf,'Cookie':'X-CSRF-Token='+csrf}
        if integration:headers['X-NSIPA-Field-Owner']=payload.requester
        response=await client.post('http://register-staff-portal-api/intake-form-data/get_intake_form_submission',json=body,headers=headers)
    if response.status_code!=200:return False
    data=response.json();content=(data.get('response_body') or {}).get('response_payload') or data.get('response_payload') or {}
    return str(content.get('submission_id'))==str(payload.artifact_id)
