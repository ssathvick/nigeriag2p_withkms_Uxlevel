import sys,json,datetime
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,'/opt/openg2p-lab/odk-sync');from odk_sync_worker import Client,ROOT
work=Path(__file__).parent;client=Client(json.loads((ROOT/'config.json').read_text()));matches=[]
try:
 for entry in client.get('/v1/projects/1/forms/nsipa_field_household_demo/submissions').json():
  raw=client.get('/v1/projects/1/forms/nsipa_field_household_demo/submissions/'+quote(entry['instanceId'],safe='')+'.xml').content
  if b'phone-gps-02' in raw.lower():
   import xml.etree.ElementTree as ET
   root=ET.fromstring(raw); matches.append({'instance':entry['instanceId'],'reference':root.findtext('.//sample_reference')}); (work/'gps-submission.xml').write_bytes(raw)
finally:client.close()
out={'checked_at_ist':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5,minutes=30))).isoformat(),'reference':'PHONE-20261110-01','odk_matches':matches};(work/'gps-receipt-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))



