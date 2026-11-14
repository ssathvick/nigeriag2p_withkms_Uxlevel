import json
from pathlib import Path
x=json.loads(Path('/opt/openg2p-lab/register-staff-portal-api-openapi.json').read_text())
p=x['paths']['/intake-form-data/save_intake_form_submission']['post'];print(json.dumps(p['requestBody']));ref=p['requestBody']['content']['application/json']['schema']['$ref'].split('/')[-1];print(ref,json.dumps(x['components']['schemas'][ref]));print(json.dumps(x['components']['schemas'].get('G2PRequestHeader')))

print(json.dumps(x['components']['schemas']['SaveIntakeFormSubmissionRequestBody']))
