# NSIPA updated project backup — 10 November 2026

This source backup supersedes the November 4 source snapshot for the included paths. Earlier design packages remain available as historical artifacts.

Includes React PBMS and registry frontend sources, beneficiary services, shared help and branding, registration services, Android v0.7 sources, ODK mapping/synchronization, review/rework fixes, test scripts and the consolidated client-concerns report. The existing backend is retained. Simulator payment tests do not certify live banking.

`source-manifest.json` records SHA-256 hashes and byte lengths relative to the repository's source root. The consolidated PDF is the authoritative current completion/pending checklist, including NPC inputs and physical-test limitations.

Excluded: runtime databases, credentials, private keys, signing keystores, live configuration, raw household/XML/GPS test receipts, screenshots, caches, dependencies, generated APKs and fault-test private connection paths. This is a source/documentation backup, not a full disaster-recovery image. Restore dependencies from package manifests; provision secrets and runtime databases separately through approved private backup procedures. Review deployment scripts before running them: they are environment-specific and can change live services. The temporary fault relay is not installed or active by this backup.

NPC attestation, production hosting/live-bank acceptance and agreed release/device coverage remain governed by the report. No new production readiness claim is made.

Historical scripts containing known runtime secret literals are sanitized with `__SET_VIA_SECURE_RUNTIME_CONFIG__`; consult the manifest for affected paths. These placeholders must be provisioned privately before those scripts can run.
