wsl -d Ubuntu-22.04 -u root -- python3 /mnt/h/Nigeria_Mosip/codex/openg2p-lab/backup-lab.py
if ($LASTEXITCODE -ne 0) { throw 'OpenG2P backup failed.' }
