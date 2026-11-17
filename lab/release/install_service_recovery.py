"""Plan/enable existing Nigeria portal services and the reporting timer at startup."""
import argparse,json,re,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true')
 p.add_argument('--services',nargs='+',default=['k3s','nginx','cloudflared','iqs-registration','pbms-react-api','iqs-beneficiary-extra'])
 p.add_argument('--timers',nargs='*',default=['iqs-analytics.timer'],help='Existing timers to enable at boot; use --timers without values to omit optional reporting timers')
 a=p.parse_args()
 if any(not re.fullmatch(r'[A-Za-z0-9_-]+',s) for s in a.services):p.error('Invalid service name')
 if any(not re.fullmatch(r'[A-Za-z0-9_-]+\.timer',s) for s in a.timers):p.error('Timer names must end in .timer')
 print(json.dumps({'apply':a.apply,'services':a.services,'boot_timers':a.timers,'recovery_interval_seconds':60,'reporting_timer_restarted_by_recovery_loop':False}))
 if not a.apply:return
 # Validate every existing unit before changing startup policy or writing recovery units.
 for unit in [s+'.service' for s in a.services]+a.timers:subprocess.run(['systemctl','cat',unit],check=True,stdout=subprocess.DEVNULL)
 root=Path('/etc/systemd/system')
 (root/'nigeria-portals-recovery.service').write_text('[Unit]\nDescription=Ensure Nigeria portal services are running\nAfter=network-online.target\n[Service]\nType=oneshot\nExecStart=/usr/bin/systemctl start '+' '.join(s+'.service' for s in a.services)+'\nTimeoutStartSec=120\n')
 (root/'nigeria-portals-recovery.timer').write_text('[Unit]\nDescription=Recover stopped Nigeria portal services\n[Timer]\nOnBootSec=60s\nOnUnitActiveSec=60s\n[Install]\nWantedBy=timers.target\n')
 subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','enable','--now',*a.services,*a.timers,'nigeria-portals-recovery.timer'],check=True)
 print('Startup/recovery enabled. Reporting timers follow their existing schedule; the recovery loop does not override an explicit timer stop. WSL still needs its Windows boot/logon task.')

if __name__=='__main__':main()
