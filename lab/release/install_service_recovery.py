"""Plan/install automatic recovery of existing Nigeria portal services on a systemd host."""
import argparse,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true')
 p.add_argument('--services',nargs='+',default=['k3s','nginx','cloudflared','iqs-registration','pbms-react-api','iqs-beneficiary-extra']);a=p.parse_args()
 if any(not s.replace('-','').replace('_','').isalnum() for s in a.services):p.error('Service names may contain only letters, numbers, hyphens and underscores')
 print('Enable existing services and recover stopped services every minute:',', '.join(a.services))
 if not a.apply:return
 # Check all requested units before changing startup policy.
 for service in a.services:subprocess.run(['systemctl','cat',service+'.service'],check=True,stdout=subprocess.DEVNULL)
 root=Path('/etc/systemd/system')
 (root/'nigeria-portals-recovery.service').write_text('[Unit]\nDescription=Ensure Nigeria portal services are running\nAfter=network-online.target\n[Service]\nType=oneshot\nExecStart=/usr/bin/systemctl start '+' '.join(s+'.service' for s in a.services)+'\nTimeoutStartSec=120\n')
 (root/'nigeria-portals-recovery.timer').write_text('[Unit]\nDescription=Recover stopped Nigeria portal services\n[Timer]\nOnBootSec=60s\nOnUnitActiveSec=60s\n[Install]\nWantedBy=timers.target\n')
 subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','enable','--now',*a.services,'nigeria-portals-recovery.timer'],check=True)
 print('Recovery enabled. WSL still requires a Windows startup/logon task to launch its distribution.')

if __name__=='__main__':main()
