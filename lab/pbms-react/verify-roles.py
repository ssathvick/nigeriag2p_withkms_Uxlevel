import json,pathlib,secrets,requests
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
fixtures=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json').read_text())
def group(module,name):return call('ir.model.data','search_read',[[['module','=',module],['name','=',name]]],{'fields':['res_id']})[0]['res_id']
base=group('base','group_user');audit=group('g2p_pbms','group_audit_operation')
allowed=call('res.groups','search',[[['name','=',fixtures[0]['tag']]]])[0]
created=[];results=[]
try:
    secret=secrets.token_urlsafe(24)
    user=call('res.users','create',[{'name':'React UAT restricted viewer','login':'react-uat-viewer-'+secrets.token_hex(5)+'@example.invalid','password':secret,'groups_id':[[6,0,[base,audit,allowed]]]}],{'context':{'no_reset_password':True}});created.append(user)
    login=call('res.users','read',[[user]],{'fields':['login']})[0]['login']
    for host in ['pbms.nigeriag2p.com','g2p-pbms.wverve.in']:
        origin='https://'+host;s=requests.Session()
        def rpc(model,method,args):return s.post(origin+'/web/dataset/call_kw/'+model+'/'+method,json={'jsonrpc':'2.0','method':'call','params':{'model':model,'method':method,'args':args,'kwargs':{}},'id':1},timeout=40).json()
        response=s.post(origin+'/web/session/authenticate',json={'jsonrpc':'2.0','method':'call','params':{'db':'pbmsdb','login':login,'password':secret},'id':1},timeout=40).json();assert response.get('result',{}).get('uid')==user
        def request(path,body=None):return s.post(origin+'/pbms-ui-api/'+path,json=body or {},headers={'Origin':origin},timeout=90)
        ok=request('workflow/'+str(fixtures[0]['enrollment_list_id']));assert ok.status_code==200,ok.text[:350]
        assert ok.json()['permissions']=={'approve':False,'verify':False}
        for endpoint in ['approve','verification']:
            denied=request(endpoint+'/'+str(fixtures[0]['enrollment_list_id']),{'comment':'must not persist'});assert denied.status_code==403,(endpoint,denied.text)
        outside=request('workflow/'+str(fixtures[1]['enrollment_list_id']));assert outside.status_code==403,outside.text
        write=rpc('g2p.program.definition','write',[[fixtures[0]['program_id']],{'description':'must not persist'}]);assert 'error' in write
        results.append({'host':host,'viewer_read':'passed','viewer_write':'denied','verification':'denied','approval':'denied','other_programme':'denied'})
        s.post(origin+'/web/session/destroy',json={'jsonrpc':'2.0','method':'call','params':{},'id':1},timeout=30)
finally:
    for user in created:call('res.users','write',[[user],{'active':False}])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/role-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
