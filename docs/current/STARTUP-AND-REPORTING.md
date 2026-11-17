# Automatic startup and geographic reporting timer — 17 November 2026

The Nigeria reporting timer was running but disabled for boot. It is now enabled and active on the original installation. The repository startup installer and launch helpers include the same persistent reporting-timer setup.

## Startup sequence

1. The existing Windows **Nigeria-G2P-Boot** task uses a boot trigger and S4U to launch the Windows owner's `Ubuntu-22.04` WSL distribution. Its action keeps WSL running; it does not store a password or recreate application credentials.
2. WSL systemd starts the enabled portal services and **iqs-analytics.timer**.
3. The reporting timer triggers **iqs-analytics.service** about two minutes after systemd boots and subsequently every 15 minutes from activation. It keeps the existing `Persistent=true` setting. The first collection depends on source services being available; failed source collections retain previous valid cache data and the timer retries on its next scheduled run.
4. The geographic reporting repair remains in place. Verify a successful collector Result and fresh source totals; the timer being active alone is not proof of a successful collection.

A successful oneshot collector normally returns to `inactive` after finishing. Check `Result=success` and `ExecMainStatus=0`; check the **timer** for active/enabled state and its next trigger.

## Apply on an existing destination

After installing the existing application services and analytics unit, inspect and apply:

```bash
sudo python3 "$SOURCE/release/install_service_recovery.py"
sudo python3 "$SOURCE/release/install_service_recovery.py" --apply
sudo systemctl is-enabled iqs-analytics.timer
sudo systemctl is-active iqs-analytics.timer
sudo systemctl list-timers --all | grep iqs-analytics
sudo systemctl show iqs-analytics.service -p Result -p ExecMainStatus
```

The helper defaults to a non-mutating plan. Apply validates all service/timer units before changing startup policy, then enables the six existing Nigeria services, the existing analytics timer and the one-minute service recovery timer. `--services` adapts the installed service list; `--timers` adapts the existing timer list. Use `--timers` without values to omit optional reporting timers on a destination that does not have analytics installed. It does not install missing application services.

The reference timer file is `release/units/iqs-analytics.timer`: OnBootSec=2min, OnUnitActiveSec=15min, Persistent=true, WantedBy=timers.target. Compare with the destination timer; retain an intentional custom schedule. A missing analytics service must be installed through the application/analytics setup first.

The recovery loop starts only its configured application services. It does **not** restart a deliberately stopped reporting timer every minute. Portal Control can still stop/start the reporting timer through its existing lifecycle actions. `Start-Lab.ps1` now starts it alongside the existing portal services.

On Windows, run `Install-BootStartup-Admin.ps1` once from elevated PowerShell as the Windows account that owns the WSL distribution. Adapt the distribution name before installation if necessary. The helper registers/starts the boot task, checks portal services and reporting timer activity, and verifies that the reporting timer is enabled for startup. It leaves a full destination reboot test as a separate acceptance step.

## Verification on the original host

Today’s Windows restart restored WSL outbound internet. NigeriaG2P, KarnatakaDBT and Shaalavatsa returned HTTP 200 with all required workloads ready. The Nigeria Windows boot task was observed running with a boot trigger. The reporting timer was subsequently enabled and checked active, and the collector's last Result was success. The geographic totals and all 15 reporting sources had passed verification after the reporting repair.

**No additional full Windows reboot was performed after enabling the reporting timer.** The new persistence setting is verified from systemd enablement and schedule configuration, rather than claiming a second cold-boot acceptance test. Destination installations should perform that final restart check after applying their own source/configuration.

No account passwords, registry records, approvals or payment states are changed by these startup updates. Application/tunnel availability still depends on working Windows/WSL networking. The prior networking failure produced Cloudflare 530/1033 even while local origins were healthy; a running tunnel process alone does not prove public reachability.

The [sanitized verification summary](../../source-snapshots/2026-11-17-startup-timer/verification-summary.json) contains current unit/task states and public HTTP outcomes without usernames, credentials or private configuration. Run `python3 "$SOURCE/release/test_service_recovery.py"` for no-cluster tests of planning, boot-timer inclusion, missing-unit validation and explicit-stop preservation.
