"""Additional boundary checks on actual persisted approval-flow records."""
import pathlib,json,datetime,xmlrpc.client,secrets,base64
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
fixtures=json.loads(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-approval-results.json').read_text())
p=fixtures['program_id'];dl=fixtures['disbursement_list_id'];checks=[]
def denied(fn,name):
 try:fn()
 except xmlrpc.client.Fault:checks.append(name);print('PASS',name,flush=True);return
 raise AssertionError('Unexpected permission: '+name)
call('g2p.program.definition','write',[[p],{'program_status':'ACTIVE'}])
# A second monthly cycle does not discard the previous cycle or audit history.
next_month=datetime.date(2026,12,1)
en=call('g2p.enrollment.cycle','create',[{'program_id':p,'cycle_number':2,'enrollment_start_date':'2026-11-01','enrollment_end_date':'2026-11-12','disbursement_start_date':'2026-12-01','disbursement_end_date':'2026-12-28'}])
el=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':en,'mnemonic':'NSIPA_BOUNDARY_DEC_'+str(en)}])
cron=call('ir.model.data','search_read',[[['module','=','nsipa_approval'],['name','=','process_lists']]],{'fields':['res_id']})[0]['res_id'];call('ir.cron','method_direct_trigger',[[cron]])
assert call('g2p.beneficiary.list','nsipa_details',[[el]])['list']['nsipa_status']=='complete'
assert call('g2p.beneficiary.list','nsipa_details',[[dl]])['list']['nsipa_status']=='verified'
checks.append('multiple monthly cycles retain earlier approved lists');print('PASS',checks[-1],flush=True)
denied(lambda:call('g2p.enrollment.cycle','create',[{'program_id':p,'cycle_number':3,'enrollment_start_date':'2026-11-01','enrollment_end_date':'2026-11-12','disbursement_start_date':'2026-12-02','disbursement_end_date':'2026-12-27'}]),'duplicate monthly cycle rejected')
denied(lambda:call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':en,'mnemonic':'DUPLICATE'}]),'duplicate list for same cycle rejected')
future=call('g2p.enrollment.cycle','create',[{'program_id':p,'cycle_number':4,'enrollment_start_date':'2027-01-01','enrollment_end_date':'2027-01-12','disbursement_start_date':'2027-01-20','disbursement_end_date':'2027-01-28'}])
denied(lambda:call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':future,'mnemonic':'TOO_EARLY'}]),'enrolment list blocked before registration window closes')
denied(lambda:call('g2p.enrollment.cycle','write',[[future],{'disbursement_start_date':'2027-01-01'}]),'invalid date correction rejected by server')
# Evidence from different programmes cannot be read using an unassigned staff session.
creds=json.loads(pathlib.Path('/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json').read_text());c=creds['finance'];u=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb',c['login'],c['password'],{})
def outsider(m,method,args=None):return xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object').execute_kw('pbmsdb',u,c['password'],m,method,args or [],{})
denied(lambda:outsider('g2p.beneficiary.list','nsipa_details',[[dl]]),'unassigned programme detail access rejected')
assert not outsider('nsipa.approval.line','search',[[['list_id','=',dl]]]);assert not outsider('nsipa.approval.event','search',[[['list_id','=',dl]]]);checks.append('record rules isolate beneficiary and evidence searches');print('PASS',checks[-1],flush=True)
# The same two Registry households are independently enrolled in the browser-test programmes.
programs=call('g2p.program.definition','search',[[['program_mnemonic','like','NSIPA_BROWSER_']]])
shared=call('nsipa.approval.line','search_read',[[['list_id.program_id','in',programs],['beneficiary_id','=','NSIPA-PRESENTATION-1']]],{'fields':['list_id']})
assert len(shared)>=4;checks.append('same beneficiary participates in multiple programmes');print('PASS',checks[-1],flush=True)
benefit=call('g2p.program.benefit.codes','search_read',[[['program_id','=',p]]],{'fields':['benefit_code_id']})[0]
denied(lambda:call('g2p.program.benefit.codes','write',[[benefit['id']],{'max_quantity':50000}]),'benefit maximum cannot be raised after list creation')
denied(lambda:call('g2p.benefit.codes','write',[[benefit['benefit_code_id'][0]],{'measurement_unit':'USD'}]),'mapped cash currency cannot change after list creation')
call('g2p.program.definition','write',[[p],{'program_status':'PAUSED'}])
for bid in programs:call('g2p.program.definition','write',[[bid],{'program_status':'PAUSED'}])
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/native-boundary-results.json').write_text(json.dumps({'status':'passed','checks':checks},indent=2))
