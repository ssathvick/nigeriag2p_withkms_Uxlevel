"""Exercise real PBMS contracts, using credentials in memory only."""
import json, pathlib, sys, time
import requests, yaml

BASE='https://'+(sys.argv[sys.argv.index('--host')+1] if '--host' in sys.argv else 'pbms.nigeriag2p.com')
session=requests.Session()
def rpc(path,params=None):
    r=session.post(BASE+path,json={'jsonrpc':'2.0','method':'call','params':params or {},'id':1},timeout=45)
    r.raise_for_status()
    body=r.json()
    if body.get('error'):
        raise RuntimeError(body['error'].get('data',{}).get('message',body['error']['message']))
    return body.get('result')
def call(model,method,args=None,kwargs=None):
    return rpc('/web/dataset/call_kw/'+model+'/'+method,{'model':model,'method':method,'args':args or [],'kwargs':kwargs or {}})

password=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
user=rpc('/web/session/authenticate',{'db':'pbmsdb','login':'admin@nigeria.openg2p.localhost','password':password})
assert user.get('uid')
if '--browser-session' in sys.argv:
    print(json.dumps([{'name':c.name,'value':c.value,'domain':BASE.split('//')[1],'path':'/','secure':True,'httpOnly':True,'sameSite':'Lax'} for c in session.cookies]))
    sys.exit(0)

checks=[]
for host in ['pbms.nigeriag2p.com','g2p-pbms.wverve.in']:
    for path in ['/','/web','/pbms-ui/','/pbms-ui/app.js','/pbms-ui/app.css']:
        r=requests.get('https://'+host+path,timeout=45)
        assert r.status_code==200,(host,path,r.status_code)
        if path in ['/','/web','/pbms-ui/']:
            assert 'id="root"' in r.text and '/pbms-ui/app.js' in r.text,(host,path)
    assert requests.get('https://'+host+'/web?native=1',timeout=45).status_code==200
    assert requests.get('https://'+host+'/web/database/manager',timeout=45).status_code==404
    checks.append(host+': React routes, assets, native fallback and database-manager block passed')
models=['g2p.program.definition','g2p.enrollment.cycle','g2p.disbursement.cycle','g2p.beneficiary.list','g2p.household.registry','g2p.farmer.registry','g2p.student.registry','g2p.eligibility.rule.definition','g2p.entitlement.rule.definition','g2p.priority.rule.definition','g2p.benefit.codes','g2p.program.benefit.codes','g2p.agency','g2p.warehouse']
for model in models:
    fields=call(model,'fields_get',[],{'attributes':['string','type','selection','relation','required','readonly','help','store']})
    records=call(model,'search_read',[[]],{'fields':['id','display_name'],'limit':1})
    assert isinstance(call(model,'search_count',[[]]),int)
    assert isinstance(call(model,'check_access_rights',['write',False]),bool)
    if records:
        names=[k for k,f in fields.items() if f['type'] not in ['binary','html'] and k!='__last_update']
        assert call(model,'read',[[records[0]['id']]],{'fields':names})
checks.append('All 14 models: metadata, listing, count, access check and detail read passed')
assert call('res.users','has_group',['g2p_pbms.group_program_editor'])
assert call('res.users','has_group',['g2p_pbms.group_program_super_administration'])
created=None
try:
    values={'program_mnemonic':'REACT_SMOKE_'+str(int(time.time())),'description':'Temporary React frontend contract test','target_registry':'household','program_status':'PAUSED','enrollment_frequency':'OnDemand','disbursement_frequency':'OnDemand','auto_approve_enrolment':False,'auto_approve_disbursement':False}
    created=call('g2p.program.definition','create',[values],{'context':{'program_form_create':True,'program_form_edit':True}})
    assert call('g2p.program.definition','write',[[created],{'description':'Temporary React frontend contract test updated'}],{'context':{'program_form_edit':True}})
    record=call('g2p.program.definition','read',[[created]],{'fields':['description']})[0]
    assert record['description'].endswith('updated')
    checks.append('Temporary paused programme create, edit and read-back passed')
finally:
    if created:
        call('g2p.program.definition','unlink',[[created]])
        assert call('g2p.program.definition','search_count',[[['id','=',created]]])==0
        checks.append('Temporary programme and its programme group cleaned up')
anonymous=requests.post(BASE+'/web/dataset/call_kw/g2p.program.definition/search_read',json={'jsonrpc':'2.0','method':'call','params':{'model':'g2p.program.definition','method':'search_read','args':[[]],'kwargs':{'limit':1}},'id':1},timeout=45)
assert anonymous.json().get('error'), 'Unauthenticated reads must fail'
checks.append('Unauthenticated record access rejected')
rpc('/web/session/destroy')
print(json.dumps({'passed':checks},indent=2))
