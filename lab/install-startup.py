import pathlib,subprocess
service='''[Unit]
Description=Refresh Nigeria OpenG2P local DNS after WSL startup
After=k3s.service nginx.service
Wants=k3s.service nginx.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /opt/openg2p-lab/refresh-network.py
RemainAfterExit=yes
TimeoutStartSec=900
[Install]
WantedBy=multi-user.target
'''
pathlib.Path('/etc/systemd/system/openg2p-lab-network.service').write_text(service)
script='''import subprocess,time,json
for attempt in range(60):
 r=subprocess.run(['kubectl','get','nodes'],capture_output=True)
 if r.returncode==0:break
 time.sleep(2)
else:raise RuntimeError('K3s did not start')
for attempt in range(30):
 subprocess.run(['kubectl','-n','istio-system','rollout','status','deploy/istiod','--timeout=20s'],capture_output=True)
 r=subprocess.run(['python3','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/repair-local-network.py'],capture_output=True)
 if r.returncode==0:break
 time.sleep(5)
else:raise RuntimeError('Local network refresh failed after startup retries')
for attempt in range(30):
 r=subprocess.run(['python3','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/sync-supporting-db-passwords.py'],capture_output=True)
 if r.returncode==0:break
 time.sleep(5)
else:raise RuntimeError('Supporting database credential synchronization failed')
'''
pathlib.Path('/opt/openg2p-lab/refresh-network.py').write_text(script)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','openg2p-lab-network'],check=True)
print('WSL startup networking repair enabled.')
