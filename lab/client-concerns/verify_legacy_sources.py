import sys,json,hashlib
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,'/opt/openg2p-lab/odk-sync');from odk_sync_worker import ROOT,Client
work=Path(__file__).parent/'legacy-verification';items=json.loads((work/'approved-mappings.json').read_text());cfg=json.loads((ROOT/'config.json').read_text());results=[]
for host in ['odk.nigeriag2p.com','g2p-odk.wverve.in']:
 config={**cfg,'odk_origin':'https://'+host};client=Client(config)
 try:
  definition=client.get('/v1/projects/1/forms/nsipa_field_household_demo/versions/2026110401.xml').content
  for item in items:
   review=item['review'];xml=client.get('/v1/projects/1/forms/nsipa_field_household_demo/submissions/'+quote(item['instance'],safe='')+'.xml').content
   assert hashlib.sha256(xml).hexdigest()==review['source_sha256'];assert hashlib.sha256(definition).hexdigest()==review['definition_sha256']
   assert b'<household_name>' not in xml and b'<household_head_name>' not in xml
   results.append({'host':host,'reference':item['sample_reference'],'original_source_unchanged':True,'archived_definition_matches':True})
 finally:client.close()
(work/'original-source-checks.json').write_text(json.dumps(results,indent=2));print('PASS ten original-source checks and archived-definition checks through both ODK domains')
