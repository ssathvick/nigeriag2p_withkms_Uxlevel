$ErrorActionPreference = 'Stop'
$certificate = Join-Path $PSScriptRoot 'openg2p-lab-ca.crt'
Import-Certificate -FilePath $certificate -CertStoreLocation Cert:\LocalMachine\Root | Out-Null
'OpenG2P lab certificate trusted for this computer.' | Set-Content (Join-Path $PSScriptRoot 'certificate-trust-status.txt')
