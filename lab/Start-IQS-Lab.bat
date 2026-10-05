@echo off
title Start IQS Nigeria G2P Lab
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-IQS-Lab.ps1"
if errorlevel 1 (
  echo.
  echo Startup did not finish. See the message above.
  pause
)
