import os
import pathlib,json,xmlrpc.client,hashlib
r=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react');exec((r.parent/'inspect-pbms-react.py').read_text().split('models =')[0])
checks=[]
def ok(s):checks.append(s);print('PASS',s,flush=True)
options=call('g2p.program.definition','nsipa_analytics_options',[]);assert options
before=call('g2p.beneficiary.list','search_read',[[['program_id.nsipa_flow','=',True]]],{'fields':['nsipa_status','nsipa_revision','nsipa_payment_hash','list_workflow_status','write_date']})
for program in options:
 for cycle in program['cycles']:
  data=call('g2p.program.definition','nsipa_geographic_analytics',[[program['id']],cycle['key']])
  assert sum(x['beneficiaries'] for x in data['states'])==data['total_beneficiaries']
  assert data['mapped_beneficiaries']+data['unmapped_beneficiaries']==data['total_beneficiaries']
  assert not any(k in json.dumps(data) for k in ['beneficiary_id','registry_id','source_json'])
ok('all programme/cycle totals reconcile; API contains aggregates only')
f=json.loads((r/'evidence/connected-payments/fixture.json').read_text());listing=call('g2p.beneficiary.list','read',[[f['list_id']]],{'fields':['disbursement_cycle_id']})[0];key='disbursement:'+str(listing['disbursement_cycle_id'][0]);d=call('g2p.program.definition','nsipa_geographic_analytics',[[f['program_id']],key]);assert d['total_beneficiaries']==1 and d['excluded_beneficiaries']==1 and d['entitlement_ngn']==1;assert d['states'][0]['payment_submitted_beneficiaries']==1
ok('approved NGN 1 snapshot and exclusion match payment flow exactly')
creds=json.loads(pathlib.Path(os.environ.get('PBMS_APPROVAL_ACCOUNTS_FILE','/opt/openg2p-lab/pbms-react/nsipa-presentation-credentials.json')).read_text());roles=[]
for role in ['admin','payment','finance','audit','ceo']:
 c=creds[role];user=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb',c['login'],c['password'],{})
 proxy=xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object')
 def actor(method,args=None):return proxy.execute_kw('pbmsdb',user,c['password'],'g2p.program.definition',method,args or [])
 visible=actor('nsipa_analytics_options');assert f['program_id'] in [p['id'] for p in visible]
 assert actor('nsipa_geographic_analytics',[[f['program_id']],key])['total_beneficiaries']==1
 roles.append(role)
 if role!='admin':
  hidden=next(p for p in options if p['id'] not in [v['id'] for v in visible] and p['cycles'])
  try:actor('nsipa_geographic_analytics',[[hidden['id']],hidden['cycles'][0]['key']])
  except xmlrpc.client.Fault:pass
  else:raise AssertionError('Unassigned programme access allowed')
ok('all five roles can access assigned programmes; unassigned programmes denied')
foreign=next(p for p in options if p['id']!=f['program_id'] and p['cycles'])
try:call('g2p.program.definition','nsipa_geographic_analytics',[[f['program_id']],foreign['cycles'][0]['key']])
except xmlrpc.client.Fault:ok('cycle from another programme rejected')
else:raise AssertionError('Foreign cycle accepted')
pl=call('nsipa.approval.line','search_read',[[['state','=','PL'],['included','=',True]]],{'fields':['list_id'],'limit':1})[0]
l=call('g2p.beneficiary.list','read',[[pl['list_id'][0]]],{'fields':['program_id','list_stage','enrollment_cycle_id','disbursement_cycle_id']})[0]
k=l['list_stage']+':'+str(l[l['list_stage']+'_cycle_id'][0]);d=call('g2p.program.definition','nsipa_geographic_analytics',[[l['program_id'][0]],k]);assert any(s['name']=='Plateau' and s['beneficiaries'] for s in d['states']);ok('stored PL state alias maps to Plateau')
after=call('g2p.beneficiary.list','search_read',[[['program_id.nsipa_flow','=',True]]],{'fields':['nsipa_status','nsipa_revision','nsipa_payment_hash','list_workflow_status','write_date']});assert before==after;ok('list approvals, revisions and payment states unchanged by analytics reads')
out=r/'evidence/geographic-analytics';out.mkdir(exist_ok=True);(out/'backend-results.json').write_text(json.dumps({'status':'passed','roles':roles,'programmes':len(options),'checks':checks},indent=2))
