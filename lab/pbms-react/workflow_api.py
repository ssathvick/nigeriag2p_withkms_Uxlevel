"""Session-bound frontend adapter. Business operations remain in existing PBMS.

Bridge 3 uses a different report envelope than the bundled Odoo report client.
This adapter translates read requests; it never writes a database or dispatches
payments directly. Approval uses the existing role-checked Odoo action.
"""
import base64, datetime, fcntl, json, os, pathlib, uuid
from flask import Flask, request, jsonify
import requests

app=Flask(__name__)
app.config['MAX_CONTENT_LENGTH']=16*1024*1024
ODOO=os.environ['PBMS_ODOO_URL']
BRIDGE=os.environ['PBMS_BRIDGE_URL']
ALLOWED=set(filter(None,os.environ.get('PBMS_ALLOWED_ORIGINS','https://pbms.nigeriag2p.com,https://g2p-pbms.wverve.in,https://pbms.openg2p.localhost').split(',')))
WIZARD='g2p.bgtask.summary.wizard'

class Problem(Exception):
    def __init__(self,message,status=400):self.message,self.status=message,status
@app.errorhandler(Problem)
def problem(e):return jsonify(error=e.message),e.status
@app.errorhandler(requests.RequestException)
def upstream_error(e):return jsonify(error='The PBMS or payment reporting service is unavailable. Refresh before trying again.'),502

class User:
    def __init__(self):
        if request.headers.get('Origin') not in ALLOWED:raise Problem('A same-origin request is required.',403)
        if not request.is_json:raise Problem('JSON is required.',415)
        self.http=requests.Session()
        cookie=request.cookies.get('session_id')
        if not cookie:raise Problem('Sign in to PBMS.',401)
        self.http.cookies.set('session_id',cookie)
        self.session=self.rpc('/web/session/get_session_info',{})
        if not self.session.get('uid'):raise Problem('Sign in to PBMS.',401)
        self.context=self.session.get('user_context',{})
    def rpc(self,path,params):
        response=self.http.post(ODOO+path,json={'jsonrpc':'2.0','method':'call','params':params,'id':1},timeout=40)
        response.raise_for_status();body=response.json()
        if body.get('error'):
            error=body['error'];expired=error.get('code')==100
            raise Problem('Your session expired. Sign in again.' if expired else error.get('data',{}).get('message','PBMS rejected this operation.'),401 if expired else 403)
        return body.get('result')
    def call(self,model,method,args=None,kwargs=None):
        kw=kwargs or {};kw['context']={**getattr(self,'context',{}),**kw.get('context',{})}
        return self.rpc('/web/dataset/call_kw/'+model+'/'+method,{'model':model,'method':method,'args':args or [],'kwargs':kw})
    def group(self,name):return self.call('res.users','has_group',['g2p_pbms.'+name])
    def listing(self,id):
        rows=self.call('g2p.beneficiary.list','read',[[id]],{'fields':['mnemonic','brief','program_id','beneficiary_list_id','enrollment_cycle_id','disbursement_cycle_id','list_stage','list_workflow_status','eligibility_process_status','entitlement_process_status','envelope_creation_status','disbursement_batch_creation_status','number_of_registrants','number_of_entitlements_processed','eligibility_latest_error_code','entitlement_latest_error_code','envelope_creation_latest_error_code','dbc_latest_error_code']})
        if not rows:raise Problem('The beneficiary list is unavailable.',404)
        row=rows[0]
        if not row['program_id']:raise Problem('This list has no linked programme.')
        program=self.call('g2p.program.definition','read',[[row['program_id'][0]]],{'fields':['program_mnemonic','target_registry','verifications_for_enrolment','verifications_for_disbursement','auto_approve_enrolment','auto_approve_disbursement']})[0]
        return row,program
    def wizard(self,row,program):
        values={'target_registry':program['target_registry'],'program_id':program['id'],'mnemonic':row['mnemonic'],'brief':row['brief'],'beneficiary_list_id':row['id'],'beneficiary_list_uuid':row['beneficiary_list_id'],'list_stage':row['list_stage'],'list_workflow_status':row['list_workflow_status'],'enrollment_cycle_id':row['enrollment_cycle_id'][0] if row['enrollment_cycle_id'] else False,'disbursement_cycle_id':row['disbursement_cycle_id'][0] if row['disbursement_cycle_id'] else False}
        return self.call(WIZARD,'create',[values])
    def verifications(self,id):
        return self.call('storage.file','search_read',[[['beneficiary_list_id','=',id]]],{'fields':['verified_by','comment','verification_timestamp','name','file_size'],'order':'id desc'})

def approved(row):return row['list_workflow_status'] in ['approved_final_enrolment','approved_for_disbursement']
def readiness(row,program,verifications):
    disbursement=row['list_stage']=='disbursement'
    required=program['verifications_for_disbursement' if disbursement else 'verifications_for_enrolment']
    ready=row['eligibility_process_status']=='complete' and (not disbursement or row['entitlement_process_status']=='complete')
    return {'required':required,'received':len(verifications),'calculation_complete':ready,'approved':approved(row),'can_approve':ready and len(verifications)>=required and not approved(row)}

@app.post('/pbms-ui-api/workflow/<int:id>')
def workflow(id):
    user=User();row,program=user.listing(id);checks=user.verifications(id)
    disbursement=row['list_stage']=='disbursement'
    auto=program['auto_approve_disbursement' if disbursement else 'auto_approve_enrolment']
    state=readiness(row,program,checks)
    # Preserve the existing PBMS zero-review automatic approval policy, using
    # its own action and the signed-in user's permissions (never an admin key).
    if auto and state['required']==0 and state['can_approve'] and user.call('g2p.beneficiary.list','check_access_rights',['write',False]):
        lock=pathlib.Path(os.environ.get('PBMS_LOCK_DIR','/run/pbms-react'))/f'approve-{id}.lock'
        with lock.open('a') as handle:
            fcntl.flock(handle,fcntl.LOCK_EX)
            fresh,_=user.listing(id)
            if not approved(fresh):
                auto_wizard=user.wizard(fresh,program)
                user.call(WIZARD,'approve_for_disbursement' if disbursement else 'approve_final_enrollment',[[auto_wizard]])
        row,program=user.listing(id)
    wid=user.wizard(row,program)
    data=user.call(WIZARD,'read',[[wid]],{'fields':['summary_line_ids','disbursement_envelope_line_ids','disbursement_batch_line_ids']})[0]
    def read(model,ids,fields):return user.call(model,'read',[ids],{'fields':fields}) if ids else []
    result={'list':row,'program':program,'verifications':checks,'readiness':readiness(row,program,checks),
      'permissions':{'verify':user.group('group_beneficiary_list_verifier') and user.call('storage.file','check_access_rights',['create',False]),'approve':user.group('group_disbursement_approver' if row['list_stage']=='disbursement' else 'group_enrolment_approver')},
      'summary':read('g2p.api.summary.line',data['summary_line_ids'],['key','value','summary_type']),
      'envelopes':read('g2p.api.disbursement.envelope.line',data['disbursement_envelope_line_ids'],['disbursement_envelope_id','benefit_code_mnemonic','number_of_beneficiaries','total_disbursement_quantity','measurement_unit']),
      'batches':read('g2p.api.disbursement.batch.line',data['disbursement_batch_line_ids'],['batch_id','disbursement_envelope_id','benefit_code_mnemonic','number_of_beneficiaries','total_disbursement_quantity','measurement_unit','disbursement_status'])}
    if row['eligibility_process_status']=='complete' and not result['summary']:raise Problem('PBMS returned no calculation summary. The reporting connection must recover before this workflow can be reviewed.',502)
    return jsonify(result)

@app.post('/pbms-ui-api/verification/<int:id>')
def verify(id):
    user=User()
    if not user.group('group_beneficiary_list_verifier'):raise Problem('Verification permission is required.',403)
    row,program=user.listing(id)
    if approved(row):raise Problem('This list has already been approved. Refresh the workflow.',409)
    if row['eligibility_process_status']!='complete':raise Problem('Wait for calculation to finish.',409)
    body=request.get_json();comment=str(body.get('comment','')).strip()
    if not comment:raise Problem('A verification comment is required.')
    fields=['backend_id','name','verified_by','beneficiary_list_id','comment']
    values=user.call('storage.file','default_get',[fields],{'context':{'default_beneficiary_list_id':id}})
    values.update({'comment':comment,'beneficiary_list_id':id,'verified_by':user.session['uid']})
    if body.get('data'):
        try:raw=base64.b64decode(body['data'],validate=True)
        except Exception:raise Problem('Invalid document encoding.')
        if len(raw)>10*1024*1024 or not raw.startswith(b'%PDF-'):raise Problem('Attach a PDF up to 10 MB.')
        values.update({'data':body['data'],'name':pathlib.PurePath(str(body.get('filename') or 'verification.pdf')).name})
    result=user.call('storage.file','create',[values],{'context':{'beneficiary_list_verification_form_edit':True,'default_beneficiary_list_id':id}})
    return jsonify(id=result)

@app.post('/pbms-ui-api/approve/<int:id>')
def approve(id):
    user=User()
    lock=pathlib.Path(os.environ.get('PBMS_LOCK_DIR','/run/pbms-react'))/f'approve-{id}.lock'
    with lock.open('a') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX)
        row,program=user.listing(id)
        disbursement=row['list_stage']=='disbursement'
        if not user.group('group_disbursement_approver' if disbursement else 'group_enrolment_approver'):raise Problem('Approval permission is required.',403)
        if approved(row):return jsonify(already_approved=True)
        checks=user.verifications(id);status=readiness(row,program,checks)
        if not status['can_approve']:raise Problem('Calculation and the required verifications must be complete before approval.',409)
        wid=user.wizard(row,program)
        user.call(WIZARD,'action_approve_for_disbursement' if disbursement else 'action_approve_final_enrollment',[[wid]])
        refreshed,_=user.listing(id)
        if not approved(refreshed):raise Problem('Approval was not confirmed by PBMS. Refresh before retrying.',502)
        return jsonify(approved=True,status=refreshed['list_workflow_status'])

@app.post('/pbms-ui-api/beneficiaries/<int:id>')
def beneficiaries(id):
    user=User();row,program=user.listing(id);wid=user.wizard(row,program)
    page=max(1,int(request.json.get('page',1)))
    result=user.call(WIZARD,'get_beneficiaries',[wid,page,25,'[]'])
    return jsonify(result.get('message',{}))

@app.post('/pbms-ui-api/payment/<int:id>')
def payment(id):
    user=User();row,program=user.listing(id)
    if row['list_stage']!='disbursement':raise Problem('Select a disbursement list.')
    if not user.group('group_disbursement_viewer'):raise Problem('Payment viewing permission is required.',403)
    wid=user.wizard(row,program)
    kind=request.json.get('kind');ref=request.json.get('reference')
    if kind not in ['batch','envelope'] or not isinstance(ref,str):raise Problem('Invalid report request.')
    model='g2p.api.disbursement.batch.line' if kind=='batch' else 'g2p.api.disbursement.envelope.line'
    field='batch_id' if kind=='batch' else 'disbursement_envelope_id'
    matched=user.call(model,'search_count',[[['wizard_id','=',wid],[field,'=',ref]]])
    if not matched:raise Problem('This payment does not belong to the accessible beneficiary list.',403)
    now=datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload={'request_header':{'sender_app_mnemonic':'OPENG2P_PBMS','sender_app_url':request.host_url.rstrip('/'),'request_id':str(uuid.uuid4()),'request_timestamp':now},'request_body':{'request_payload':ref}}
    signature=user.call('keymanager.provider','jwt_sign_keymanager',[[],json.dumps(payload,separators=(',',':'),sort_keys=True)])
    endpoint='/get_disbursement_batch_control' if kind=='batch' else '/get_disbursement_envelope_status'
    response=requests.post(BRIDGE+endpoint,json=payload,headers={'Signature':signature},timeout=30)
    response.raise_for_status();body=response.json()
    if body.get('response_header',{}).get('response_status')!='SUCCESS':raise Problem('Bridge could not return this payment report.',502)
    report=body.get('response_body',{}).get('response_payload')
    if report is None:
        return jsonify(report_status='PENDING',message='Bridge has accepted the request, but its payment status record is not yet available. Refresh the report shortly.'),202
    return jsonify(report)

@app.after_request
def headers(response):
    response.headers['Cache-Control']='no-store'
    response.headers['X-Content-Type-Options']='nosniff'
    return response
