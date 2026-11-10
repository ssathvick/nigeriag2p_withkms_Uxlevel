"""Transfer connection privately, configure Superset, always remove its temporary file."""
import subprocess
from pathlib import Path
root=Path('/opt/openg2p-lab/registration');src=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
command=['kubectl','-n','nigeria','exec','-i','deploy/commons-services-superset','-c','superset','--']
try:
 subprocess.run(command+['sh','-c','umask 077; cat > /tmp/iqs-analytics-connection.json'],input=(root/'analytics-connections.json').read_bytes(),check=True)
 result=subprocess.run(command+['python'],input=(src/'configure-superset-analytics.py').read_bytes(),capture_output=True)
 if result.returncode:
  # Superset exceptions may include a connection URI. Retain diagnostics privately.
  (root/'analytics-superset-install.log').write_bytes(result.stdout+result.stderr)
  (root/'analytics-superset-install.log').chmod(0o600)
  raise RuntimeError('Superset configuration failed; diagnostic log retained privately.')
 print('Superset dataset connection and analytics dashboard installed.')
finally:
 subprocess.run(command+['rm','-f','/tmp/iqs-analytics-connection.json'],check=True)
