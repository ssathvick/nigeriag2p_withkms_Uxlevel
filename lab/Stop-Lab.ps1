# Stops OpenG2P services in Ubuntu; does not shut down other WSL distributions or Hyper-V VMs.
wsl -d Ubuntu-22.04 -u root -- bash -lc 'systemctl stop nginx openg2p-lab-network; /usr/local/bin/k3s-killall.sh >/opt/openg2p-lab/stop.log 2>&1'
Write-Host 'OpenG2P containers stopped. Persistent lab data is retained.'
