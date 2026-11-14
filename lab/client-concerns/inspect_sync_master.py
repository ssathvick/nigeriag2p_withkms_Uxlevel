import json
from pathlib import Path
for name in ['commons-services-master-data-api-openapi.json','register-staff-portal-api-openapi.json']:
 x=json.loads(Path('/opt/openg2p-lab/'+name).read_text());print(name,[k for k in x['paths'] if 'attribute' in k])
