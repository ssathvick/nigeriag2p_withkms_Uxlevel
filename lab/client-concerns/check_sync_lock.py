import fcntl,subprocess
from pathlib import Path
with open('/opt/openg2p-lab/odk-sync/worker.lock','a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 result=subprocess.run(['/opt/openg2p-lab/registration-venv/bin/python','/opt/openg2p-lab/odk-sync/odk_sync_worker.py'],capture_output=True,text=True,timeout=20)
 assert result.returncode==0;assert 'Another worker holds the lock' in result.stderr
 print('PASS second worker skipped while exclusive lock was held')
