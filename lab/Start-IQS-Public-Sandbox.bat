@echo off
title Start IQS Nigeria Public Sandbox
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-IQS-Lab.ps1" -HomeUrl "https://nigeriag2p.com/"
if errorlevel 1 pause
