exec(open('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/test-pbms-enrollment.py').read().split('program=')[0])
for model in ['g2p.beneficiary.list','g2p.disbursement.cycle']:
 fields=call(model,'fields_get',[],{'attributes':['type','selection','required']})
 print(model,fields)
 print(call(model,'search_read',[[]],{'limit':3}))
