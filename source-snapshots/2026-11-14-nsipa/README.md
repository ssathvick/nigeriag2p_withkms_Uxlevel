# Current NSIPA source release — 14 November 2026

Read the repository README and docs/current/INSTALLATION.md. This release supersedes the November 11 application source for the included files. Historical archives remain unchanged.

Includes current native Master Registry UI and household/individual journeys, five native Registry roles, independent Registry/AWE reviews and history, final consent/survey fields without the enumerator selector, authenticated staff/Collect utilities, updated personas/navigation/help/branding, and the native Odoo PBMS programme-to-disbursement workflow with five accounts, scheduled list processing, rejection/correction/revision history and final binary XLS export.

source-manifest.json hashes the current source files relative to source_root. Runtime-images.json records image references observed on the original installation; local nsipa image tags must be rebuilt from source. The latter is an inventory, not a complete chart/deployment or immutable image lock. The current install guide states the native schema/version prerequisites and clean-machine validation boundary.

Excluded from this source release: passwords, keys, tokens, kubeconfig, runtime databases/backups, account manifests, ODK App User URLs/QRs, private test evidence, dependencies/build caches, Camtasia files, voice samples, narration WAVs and XLS exports. Obtain exact runtime state only from a separately encrypted private backup. Use new identities, domain settings and secrets for a fresh install.

The current native Registry/AWE workflow supersedes the historical supplemental MBR writer/importer. Earlier migration source is retained for historical recovery and must not be run as a new installation sequence. The current PBMS export policy does not dispatch payments. The established NSIPA logo with words and all sections reserved for later removal are retained.
