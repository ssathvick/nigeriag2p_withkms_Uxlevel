import pathlib,json
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
for m in ['g2p.household.registry','g2p.farmer.registry','res.groups','g2p.benefit.codes']:
 meta=call(m,'fields_get',[],{'attributes':['string','type','selection']})
 print(m,json.dumps(meta if m!='res.groups' else {k:v for k,v in meta.items() if k in ['name','users','category_id']}))
print('groups',call('ir.model.data','search_read',[[['module','=','g2p_pbms'],['model','=','res.groups']]],{'fields':['name','res_id']}))
rows=call('g2p.beneficiary.list','search_read',[[['list_stage','=','disbursement'],['eligibility_process_status','=','complete']]],{'fields':['mnemonic','program_id','beneficiary_list_id','enrollment_cycle_id','disbursement_cycle_id','list_stage','brief','list_workflow_status'],'limit':1,'order':'id desc'})
if rows:
 row=rows[0];p=call('g2p.program.definition','read',[[row['program_id'][0]]],{'fields':['target_registry']})[0]
 vals={k:(v[0] if isinstance(v,list) else v) for k,v in row.items() if k in ['mnemonic','program_id','enrollment_cycle_id','disbursement_cycle_id','list_stage','brief','list_workflow_status']};vals.update(target_registry=p['target_registry'],beneficiary_list_id=row['id'],beneficiary_list_uuid=row['beneficiary_list_id']);w=call('g2p.bgtask.summary.wizard','create',[vals]);result=call('g2p.bgtask.summary.wizard','get_beneficiaries',[w,1,1,'[]']);print('beneficiary schema',json.dumps({k:([list(x.keys()) for x in v] if k=='beneficiaries' else v) for k,v in result.get('message',{}).items()}))
