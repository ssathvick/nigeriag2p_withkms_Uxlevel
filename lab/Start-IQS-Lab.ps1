param([string]$HomeUrl = 'https://openg2p.localhost/')
$ErrorActionPreference = 'Stop'
$labMutex = New-Object System.Threading.Mutex($false, 'Local\IQSNigeriaLabStartup')
$labOwnsMutex = $false
try {
    $labOwnsMutex = $labMutex.WaitOne(0)
    if (-not $labOwnsMutex) {
        Write-Host 'Another IQS lab startup is already running. Please wait for that window.'
        exit 0
    }
    Write-Host 'Starting IQS Nigeria G2P services in Ubuntu-22.04...'
    Write-Host 'After a machine restart, startup can take several minutes. Keep this window open.'
    $labLogDirectory = Join-Path $PSScriptRoot 'startup-logs'
    New-Item -ItemType Directory -Force -Path $labLogDirectory | Out-Null
    $labRunStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    Start-Process -FilePath 'wsl.exe' -WindowStyle Hidden -ArgumentList '-d Ubuntu-22.04 -u root -- bash /opt/openg2p-lab/start-lab-host.sh' -RedirectStandardOutput (Join-Path $labLogDirectory "$labRunStamp-host.log") -RedirectStandardError (Join-Path $labLogDirectory "$labRunStamp-host-error.log") | Out-Null
    & wsl.exe -d Ubuntu-22.04 -u root -- python3 /opt/openg2p-lab/wait-lab-ready.py
    if ($LASTEXITCODE -ne 0) { throw 'The services are not ready. Review the diagnostics above and the startup-logs folder.' }
    Write-Host ''
    Write-Host 'IQS Nigeria G2P is ready. Opening your home page...'
    & wsl.exe -d Ubuntu-22.04 -u root -- systemctl start cloudflared
    if ($LASTEXITCODE -ne 0) { throw 'The Cloudflare connector could not start.' }
    & wsl.exe -d Ubuntu-22.04 -u root -- systemctl start iqs-registration.service iqs-registration-sync.timer
    if ($LASTEXITCODE -ne 0) { throw 'The beneficiary registration integration could not start.' }
    Start-Process $HomeUrl
    Write-Host 'You can close this window. Services continue running until Windows/WSL shuts down or you stop the lab.'
} catch {
    Write-Host "Startup error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    if ($labOwnsMutex) { $labMutex.ReleaseMutex() }
    $labMutex.Dispose()
}
