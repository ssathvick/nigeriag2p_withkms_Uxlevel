# Run once from an elevated PowerShell window as the Windows user who owns Ubuntu-22.04.
# S4U starts this user's WSL distribution before interactive sign-in; no password is stored.
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
if (-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Open PowerShell with Run as administrator, then run this script again.'
}
$action = New-ScheduledTaskAction -Execute "$env:WINDIR\System32\wsl.exe" -Argument '-d Ubuntu-22.04 -u root --exec /bin/sleep infinity'
$principal = New-ScheduledTaskPrincipal -UserId $identity.Name -LogonType S4U -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName 'Nigeria-G2P-Boot' -Action $action -Trigger (New-ScheduledTaskTrigger -AtStartup) -Principal $principal -Settings $settings -Description 'Start Nigeria G2P WSL services at machine startup' -Force | Out-Null
Start-ScheduledTask -TaskName 'Nigeria-G2P-Boot'
Start-Sleep -Seconds 8
$task = Get-ScheduledTask -TaskName 'Nigeria-G2P-Boot'
$info = Get-ScheduledTaskInfo -TaskName 'Nigeria-G2P-Boot'
if ($task.State -ne 'Running') { throw "Boot task did not remain running. Last result: $($info.LastTaskResult)" }
wsl.exe -d Ubuntu-22.04 -u root -- systemctl is-active k3s nginx cloudflared iqs-registration pbms-react-api iqs-beneficiary-extra nigeria-portals-recovery.timer
if ($LASTEXITCODE -ne 0) { throw 'One or more portal services are not active.' }
Write-Host 'Nigeria G2P boot task installed and verified running. A full reboot test remains to be done.'
