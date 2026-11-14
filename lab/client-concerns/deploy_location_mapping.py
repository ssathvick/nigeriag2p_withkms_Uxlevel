"""Back up and atomically replace mapper files under the worker's own lock."""
import datetime,fcntl,os,shutil,ast,hashlib,json
from pathlib import Path
src=Path(__file__).parent;dest=Path('/opt/openg2p-lab/odk-sync')
names=['odk_geography.py','odk_household_mapping.py','odk_sync_worker.py']
for name in names:ast.parse((src/name).read_text())
os.umask(0o077)
backup=Path('/opt/openg2p-lab/backups')/('location-mapping-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
backup.mkdir()
with open(dest/'worker.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for name in names:
  if (dest/name).exists():shutil.copy2(dest/name,backup/name)
 for name in names:
  target=dest/(name+'.new');shutil.copy2(src/name,target);os.replace(target,dest/name)
 (backup/'deployment.json').write_text(json.dumps({name:hashlib.sha256((dest/name).read_bytes()).hexdigest() for name in names},indent=2))
print('Mapper deployed; backup:',backup)
