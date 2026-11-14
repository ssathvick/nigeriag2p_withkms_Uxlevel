import json,sys
from pathlib import Path
exec((Path(__file__).parent/'inspect_demo_roles.py').read_text().split('user=s.get')[0])
for cid in ['register-staff-portal','odk-central']:
 xs=s.get(base+'/clients',params={'clientId':cid}).json()
 print(cid,[(x.get('clientId'),x.get('directAccessGrantsEnabled'),x.get('publicClient'),x.get('serviceAccountsEnabled')) for x in xs])
d=json.loads(Path('/opt/openg2p-lab/register-staff-portal-api-openapi.json').read_text());print([k for k in d['paths'] if 'intake' in k or 'attributes/values' in k]);print(d.get('components',{}).get('securitySchemes'))
