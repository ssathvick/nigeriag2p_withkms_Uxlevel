wsl -d Ubuntu-22.04 -u root -- bash -lc 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml; systemctl is-active k3s nginx; kubectl get deploy,sts -n nigeria; helm list -n nigeria'
