# Prints the private, pre-seeded MBR demo credentials only when explicitly run.
wsl -d Ubuntu-22.04 -u root -- cat /opt/openg2p-lab/registration/mbr-demo-credentials.json
