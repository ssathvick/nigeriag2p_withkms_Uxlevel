"""Isolated one-beneficiary fixtures; existing local Example Bank only."""
import datetime,json,pathlib,subprocess,time
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
# Assert payment connectors cannot reach a live rail before creating test fixtures.
code="""
from urllib.parse import urlparse
from openg2p_g2p_bridge_celery_workers.app import Initializer
Initializer()
from openg2p_g2p_bridge_bank_connectors.config import Settings
c=Settings.get_config()
assert all(urlparse(getattr(c,k)).hostname=='openg2p-g2p-bridge-example-bank-api' for k in ['funds_available_check_url_example_bank','funds_block_url_example_bank','funds_disbursement_url_example_bank'])
print('LOCAL_SIMULATOR_CONFIRMED')
"""
checked=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/bridge-celery-worker','--','python','-'],input=code,text=True,capture_output=True,check=True)
assert 'LOCAL_SIMULATOR_CONFIRMED' in checked.stdout
print('Existing payment connectors verified: local Example Bank simulator only.',flush=True)
existing=call('g2p.program.definition','search',[[['program_mnemonic','=','NG_LAB_FARMER']]])[0]
benefit=call('g2p.benefit.codes','search',[[['benefit_mnemonic','=','NG_LAB_CASH']]])[0]
farmer=call('g2p.farmer.registry','search_read',[[['link_registry_id','=','NG-LAB-001']]],{'fields':['link_registry_id'],'limit':1})
if not farmer:farmer=call('g2p.farmer.registry','search_read',[[['link_registry_id','like','NG-LAB-']]],{'fields':['link_registry_id'],'limit':1})
assert farmer and farmer[0]['link_registry_id'].startswith('NG-LAB-')
domain=repr([('link_registry_id','=',farmer[0]['link_registry_id'])])
routes=call('g2p.warehouse.program.benefit.codes','search_read',[[['program_id','=',existing],['benefit_code_id','=',benefit]]],{'fields':['warehouse_id','additional_info']})
assert routes,'Existing simulator sponsor routing is required'
stores=call('storage.backend','search_read',[[]],{'fields':['name'],'limit':10})
print('Document store options:',stores)
assert stores,'Existing document storage backend required'
prior=call('ir.config_parameter','get_param',['g2p_pbms.document_store'])
if not prior:
    backup=pathlib.Path('/opt/openg2p-lab/pbms-react/backups/document-store-before.json')
    if not backup.exists():backup.write_text(json.dumps({'g2p_pbms.document_store':prior}));backup.chmod(0o600)
    call('ir.config_parameter','set_param',['g2p_pbms.document_store',str(stores[0]['id'])])
out=[];stamp=str(int(time.time()));today=datetime.date.today();end=today+datetime.timedelta(days=30)
for index,host in enumerate(['pbms.nigeriag2p.com','g2p-pbms.wverve.in']):
    tag='REACT_UAT_'+stamp+'_'+str(index)
    program=call('g2p.program.definition','create',[{'program_mnemonic':tag,'description':'Isolated React workflow UAT. One fictional beneficiary; local bank simulator; NGN 1.','target_registry':'farmer','program_status':'ACTIVE','service_providers_required':False,'enrollment_frequency':'OnDemand','disbursement_frequency':'OnDemand','verifications_for_enrolment':1,'verifications_for_disbursement':1,'auto_approve_enrolment':False,'auto_approve_disbursement':False}])
    call('g2p.program.benefit.codes','create',[{'program_id':program,'benefit_code_id':benefit,'max_quantity':1.0}])
    for r in routes:call('g2p.warehouse.program.benefit.codes','create',[{'program_id':program,'benefit_code_id':benefit,'warehouse_id':r['warehouse_id'][0],'additional_info':r['additional_info']}])
    call('g2p.eligibility.rule.definition','create',[{'program_id':program,'target_registry':'farmer','mnemonic':tag+'_ELIG','rule_number':1,'set_operator':'NONE','pbms_domain':domain}])
    call('g2p.entitlement.rule.definition','create',[{'program_id':program,'target_registry':'farmer','mnemonic':tag+'_BENEFIT','benefit_code_id':benefit,'quantity':1.0,'pbms_domain':domain}])
    cycle=call('g2p.enrollment.cycle','create',[{'program_id':program,'cycle_number':1,'enrollment_start_date':str(today),'enrollment_end_date':str(end),'disbursement_start_date':str(today),'disbursement_end_date':str(end)}])
    listing=call('g2p.beneficiary.list','create',[{'enrollment_cycle_id':cycle,'mnemonic':tag+'_ENROLL','brief':'React UAT enrollment; synthetic single-beneficiary fixture.'}])
    out.append({'host':host,'tag':tag,'program_id':program,'enrollment_cycle_id':cycle,'enrollment_list_id':listing,'expected_beneficiaries':1,'expected_quantity':1,'benefit_id':benefit})
path=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence/workflow-fixtures.json');path.write_text(json.dumps(out,indent=2))
print('Created two isolated fixture sets:',json.dumps(out),flush=True)
