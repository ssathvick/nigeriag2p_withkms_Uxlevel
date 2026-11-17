# Geographic reporting refresh repair source update - 17 November 2026

Repairs the scheduled Geographic record data source through a fixed aggregate-only SQL function and the existing three reporting views. Native invoker security, row policies, data, roles, credentials and approval/payment flows are unchanged. All 15 reporting sources are healthy on the original lab.

Read docs/current/GEOGRAPHIC-REPORTING-FIX.md and INSTALLATION.md. The narrow source helper defaults to a non-mutating plan; existing-site apply avoids fixture creation and unrelated provisioning. source-manifest.json hashes current canonical Git contents; runtime-images.json is an observed image inventory only. Earlier snapshots remain historical. verification-summary.json excludes private credentials, configurations and backups.
