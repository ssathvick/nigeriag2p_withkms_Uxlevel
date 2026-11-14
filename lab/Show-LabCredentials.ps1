# Display only on your local terminal. Do not share this output or commit it.
wsl -d Ubuntu-22.04 -u root -- cat /opt/openg2p-lab/credentials.yaml
Write-Host 'PBMS and Social Registry username: admin@nigeria.openg2p.localhost'
Write-Host 'Keycloak and staff single sign-on username: admin'
Write-Host 'Beneficiary local demo username: fatima (choose SIGN IN TO LOCAL DEMO)'
Write-Host 'Beneficiary demo uses the admin_password shown above. All identities are synthetic.'
