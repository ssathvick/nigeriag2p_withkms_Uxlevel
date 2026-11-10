"""Restore the pre-React Nginx routing without changing any PBMS data."""
from pathlib import Path
import datetime, shutil, subprocess

root=Path('/opt/openg2p-lab/pbms-react')
public_baseline=root/'backups/20261110-115925/iqs-wverve'
tls_baseline=root/'backups/20261110-120142/openg2p-lab'
assert public_baseline.is_file() and tls_baseline.is_file(), 'Baseline snapshots missing'
targets=[Path('/etc/nginx/sites-available/iqs-wverve'),Path('/etc/nginx/sites-available/openg2p-lab'),Path('/etc/nginx/conf.d/pbms-react.conf')]
backup=root/'backups'/('before-rollback-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True,mode=0o700)
previous={p:p.read_bytes() if p.exists() else None for p in targets}
for p,data in previous.items():
    if data is not None:(backup/p.name).write_bytes(data)
try:
    shutil.copy2(public_baseline,targets[0])
    shutil.copy2(tls_baseline,targets[1])
    targets[2].unlink(missing_ok=True)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
except Exception:
    for p,data in previous.items():
        if data is None:p.unlink(missing_ok=True)
        else:p.write_bytes(data)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
    raise
print('Pre-React frontend routing restored. Recovery snapshot:',backup)
