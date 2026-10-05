import json
d=json.load(open('/opt/openg2p-lab/bridge-api-openapi.json'))
for k,v in d['components']['schemas'].items():
 if any(s in k for s in ['DisbursementEnvelopeRequest','DisbursementEnvelopeResponse','DisbursementRequest','DisbursementResponse','RequestHeader','RequestBody','ResponseBody']):print(k,json.dumps(v))
