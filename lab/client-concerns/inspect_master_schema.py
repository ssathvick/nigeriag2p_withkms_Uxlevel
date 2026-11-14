import json
from pathlib import Path
x=json.loads(Path('/opt/openg2p-lab/commons-services-master-data-api-openapi.json').read_text())
for k,v in x['components']['schemas'].items():
 if 'GetAttributeValuesRequest' in k or k=='G2PPaginationRequest':print(k,json.dumps(v))
