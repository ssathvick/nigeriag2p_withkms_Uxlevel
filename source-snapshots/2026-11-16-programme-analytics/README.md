# Programme geographic analytics source update — 16 November 2026

Adds a read-only, programme-scoped Nigeria state/FCT map to PBMS with programme and enrolment/disbursement cycle filters. All five PBMS roles have access within existing programme permissions. Counts and amounts use included approval-flow list snapshots, preserving corrections/exclusions; missing states remain unmapped. LGA/GPS coverage is not claimed. The main-panel map and existing approval/payment actions are unchanged.

Read docs/current/PROGRAMME-ANALYTICS.md and INSTALLATION.md. source-manifest.json hashes the canonical Git contents under source_root. runtime-images.json lists observed images; native analytics is a persisted source mount and the frontend is a static build. Earlier dated snapshots remain historical. verification-summary.json contains sanitized original-lab outcomes, without private accounts, record IDs, screenshots or data exports.
