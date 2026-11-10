import json,pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
rows=call('g2p.beneficiary.list','search_read',[[['list_workflow_status','=','approved_for_disbursement']]],{'fields':['id','mnemonic','disbursement_batch_creation_status'],'limit':5})
print(rows)
for row in rows:
    a=call('g2p.beneficiary.list','action_open_summary_wizard',[[row['id']]])
    w=call(a['res_model'],'read',[[a['res_id']]],{'fields':['summary_line_ids','disbursement_envelope_line_ids','disbursement_batch_line_ids','verification_ids']})[0]
    print('Wizard',w)
    if w['disbursement_batch_line_ids']:
        report=call('g2p.api.disbursement.batch.line','action_view_disbursement_batch',[[w['disbursement_batch_line_ids'][0]]])
        print('Report action',json.dumps(report));break
