"""Verify archive hashes and privately check for known runtime secret values."""
import io,json,re,sys,zipfile
from pathlib import Path
import yaml
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
base=Path('/mnt/h/Nigeria_Mosip/codex');target=base/'outputs/phase1_client_review/NigeriaG2P_Phase1_Sandbox_UAT_Pack.zip'
secrets=set()
def walk(value,key=''):
 if isinstance(value,dict):
  for k,v in value.items():walk(v,str(k))
 elif isinstance(value,list):
  for v in value:walk(v,key)
 elif isinstance(value,str) and len(value)>=8 and re.search(r'password|secret|token',key,re.I):secrets.add(value.encode())
for path in [Path('/opt/openg2p-lab/credentials.yaml'),r.ROOT/'config.json',r.ROOT/'test-account.json']:
 if path.exists():walk(yaml.safe_load(path.read_text()))
count=0
def check_bytes(name,data,depth=0):
 global count
 count+=1
 if any(secret in data for secret in secrets):raise RuntimeError('A private runtime secret matched the archive. Delivery stopped.')
 if depth<2 and name.endswith(('.docx','.zip')):
  with zipfile.ZipFile(io.BytesIO(data)) as nested:
   for child in nested.namelist():check_bytes(child,nested.read(child),depth+1)
with zipfile.ZipFile(target) as z:
 manifest=json.loads(z.read('manifest.json'))
 for item in manifest['files']:
  data=z.read(item['file']);assert __import__('hashlib').sha256(data).hexdigest()==item['sha256'];check_bytes(item['file'],data)
 assert z.testzip() is None
report={'scope':'Explicit archive manifest hashes, ZIP integrity and private comparison with known runtime secret values','archive_files':len(manifest['files']),'entries_scanned_including_nested_documents':count,'known_runtime_secret_match':False,'status':'passed','limitation':'Checks known runtime secret values; does not replace a broad data classification review.'}
(base/'openg2p-lab/phase1-evidence/package-security.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
