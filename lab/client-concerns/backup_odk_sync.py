import os,shutil,sqlite3,datetime
from pathlib import Path
os.umask(0o077)
root=Path('/opt/openg2p-lab/odk-sync');dest=Path('/opt/openg2p-lab/backups')/('odk-sync-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));dest.mkdir(mode=0o700)
for name in ['config.json','odk_sync_worker.py','odk_household_mapping.py','odk_legacy_mapping.py','ODK-Synchronization-Operations.txt']:
 shutil.copy2(root/name,dest/name)
for name in ['nsipa-odk-sync.service','nsipa-odk-sync.timer']:shutil.copy2(Path('/etc/systemd/system')/name,dest/name)
a=sqlite3.connect(root/'ledger.sqlite');b=sqlite3.connect(dest/'ledger.sqlite');a.backup(b);a.close();b.close()
shutil.copytree(root/'receipts',dest/'receipts')
if (root/'legacy-review').exists():shutil.copytree(root/'legacy-review',dest/'legacy-review')
if (root/'invalid-code-review').exists():shutil.copytree(root/'invalid-code-review',dest/'invalid-code-review')
Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/client-concerns/auto-sync-verification/backup-location.txt').write_text(str(dest))
print('Private synchronization backup created')
