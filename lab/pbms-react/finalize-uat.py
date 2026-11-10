import datetime,json,pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/evidence')
fixtures=json.loads((root/'workflow-fixtures.json').read_text())
for f in fixtures:
    record=call('g2p.program.definition','read',[[f['program_id']]],{'fields':['program_mnemonic']})[0]
    assert record['program_mnemonic']==f['tag'] and f['tag'].startswith('REACT_UAT_')
    call('g2p.program.definition','write',[[f['program_id']],{'program_status':'PAUSED'}])
for name in ['workflow-browser-results.json','config-browser-results.json','role-results.json','role-action-results.json','payment-results.json','auto-policy-results.json','auto-payment-results.json']:
    assert (root/name).is_file(),name
summary={'completed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'domains':[f['host'] for f in fixtures],'screens':21,'backend_application_code_replaced':False,'backend_schema_changed':False,'authenticated_frontend_adapter_added':True,'manual_simulator_payments_reconciled':2,'automatic_simulator_payment_dispatch_verified':True,'test_programmes_paused':[f['program_id'] for f in fixtures],'audit_records_retained':True,'real_payment_rails_tested':False,'evidence':['workflow-browser-results.json','config-browser-results.json','role-results.json','role-action-results.json','payment-results.json','auto-policy-results.json','auto-payment-results.json']}
(root/'migration-results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
