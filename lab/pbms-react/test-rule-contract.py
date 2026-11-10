import pathlib
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react/verify-api.py').read_text().split('checks=[]')[0])
for model in ['g2p.eligibility.rule.definition','g2p.entitlement.rule.definition','g2p.priority.rule.definition']:
    for domain in ["[('link_registry_id','=','NG-LAB-001')]",'invalid domain']:
        result=call(model,'onchange',[[],{'target_registry':'farmer','pbms_domain':domain},['target_registry','pbms_domain'],{'sql_query':{}}])
        print(model,'valid' if domain.startswith('[') else 'invalid',result.get('value',{}).get('sql_query'))
