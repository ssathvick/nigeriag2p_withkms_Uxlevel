#!/usr/bin/env bash
set -euo pipefail
systemctl --no-block start k3s.service nginx.service openg2p-lab-network.service
# A detached Windows WSL client keeps the distribution running after the launcher exits.
# flock prevents duplicate keepalive processes when the batch file is clicked again.
flock -n /run/iqs-lab-keepalive.lock tail -f /dev/null || true
