$ErrorActionPreference = 'Stop'
Start-Process wsl.exe -WindowStyle Hidden -ArgumentList '-d Ubuntu-22.04 -u root -- bash -lc "systemctl start k3s nginx openg2p-lab-network; exec tail -f /dev/null"'
Write-Host 'OpenG2P is starting. Allow 2-4 minutes after a cold start.'
Write-Host 'Open https://openg2p.localhost in your browser.'
