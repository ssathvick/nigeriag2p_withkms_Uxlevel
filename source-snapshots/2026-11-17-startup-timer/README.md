# Automatic startup and geographic reporting timer - 17 November 2026

Updates the existing-service startup installer to enable the analytics timer at boot, updates the manual/Windows launch helpers to include/check that timer, and supplies its two-minute/15-minute reference schedule. Reporting timers are excluded from repeated service recovery, preserving deliberate stop actions. No database, role, credential or payment changes.

Read docs/current/STARTUP-AND-REPORTING.md and INSTALLATION.md. The original Windows reboot and running boot task were observed; the reporting timer was enabled afterward. No second full reboot after enablement was performed. The source includes no-cluster installer tests and sanitized live verification. Earlier snapshots remain historical. source-manifest.json hashes canonical Git contents; runtime-images.json remains an observed inventory, not an immutable deployment lock.
