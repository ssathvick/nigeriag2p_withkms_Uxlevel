# Current source update — 15 November 2026

This update adds explicit Payment submission of the same CEO-approved PBMS beneficiary list, native payment-worker snapshot integration, linked dispatch/reconciliation reports, corrected-amount/exclusion preservation, idempotency, sponsor routing locks and whole-NGN validation. The eleven marked PBMS sidebar links are hidden while supporting workflow routes and data remain. Existing login credentials are unchanged.

The source also includes existing-host automatic service recovery and an administrator-only Windows boot-task setup script. Before-sign-in startup and a full machine reboot were not tested; see the installation guide.

`source-manifest.json` hashes the current source under `source_root`; earlier dated snapshots describe historical overlays. `runtime-images.json` records observed images only; payment worker and addon mounts are installed from version-checked source. This does not replace the base platform or provide runtime databases, identities or secrets.

Read docs/current/PBMS-PAYMENTS.md and docs/current/INSTALLATION.md. verification-summary.json contains sanitized outcomes from the original synthetic local-bank tests; it is not a fresh-machine or real-bank certification.
