# Master Registry workflow

## Current authority — 12 November 2026

The native Master Registry at https://g2p-register.wverve.in/en is the sole entry point for intake, master records, change requests and approvals. The supplemental `/registration/mbr` interface is retired and redirects here; its write API returns HTTP 410. The import timer and supplemental ownership triggers are disabled. Historical native records, AWE requests, tasks, decisions and events remain in their original tables. Migration archives are retained for reconciliation.

The five accounts from `H:\Nigeria_Mosip\Credentials\mbr_demo_credentials.json` use the existing staff realm and native `register-staff-portal` client. Their native roles are Registry Officer, Registry Field Agent, Registry First Reviewer, Registry Second Reviewer and Registry Administrator. Permissions are stored in native IAM. The administrator has IAM administration access, registry configuration and read access, without intake edit or approval privileges. New household and individual intake and change requests use versioned native AWE policies assigned to Abutu for stage 1 and Adaku for stage 2, with self approval and repeated reviewers prohibited. Existing policy versions and approval history are retained.

One saved supplemental draft is preserved under the same UUID and reference in native intake. Its full original record remains in `g2p_native_workflow_legacy_drafts` and the supplemental archive; supported address and coordinate fields are copied into the native draft. Fields absent from the native schema remain preserved in that original record.

Provisioning: `integrate_native_registry_accounts.py`. Cutover: `restore_native_registry_authority.py`. Browser evidence: `output/native-registry-account-verification/results.json`. Passwords are read privately from the supplied file and never included in verification reports.

The following sections describe the retired supplemental implementation for recovery reference, not the current production entry point.

### Meeting alignment release

The 12 November meeting changes are implemented in `registry-ui-source` and native Registry/AWE module adapters under `meeting-native`. The native screens now include status filters, direct counter links, rounded status badges, compact references, UUID reveal/copy, section guidance, full review history and in-registry staff onboarding. Return for correction is a distinct AWE action; permanent rejection remains locked. Corrected changes retain their request ID and start a fresh native review attempt. Original AWE decisions and their comments are exposed in the native history view through retained migration archives.

Offline setup is `/en/offline`; staff administration is `/en/configuration/registry/users`. Both use the supplied native roles and authenticated server endpoints. Private Collect QR settings enable automatic sending on Wi-Fi/mobile and retain sent copies. `nsipa_registry_household` is the validated full household field form; its scheduled importer writes native household/member/asset sections and cannot approve them. The device-local airplane-mode/reconnect acceptance check remains outstanding because no Android device was connected.

Deployment order: capture existing modules with `capture_meeting_backend_sources.py`, prepare adapters with `prepare_meeting_native_backend.py`, apply additive schema and module mounts with `deploy_meeting_native_backend.py`, then build `registry-ui-source/Dockerfile.native` and run `deploy_meeting_native_ui.py` only after the image build completes. `native_offline_setup.py` requires `qrcode` in the existing registration virtual environment. Utility installation and field-form publication use `deploy_native_offline_setup.py`, `deploy_native_registry_users.py`, and `publish_native_collect_form.py`. Keep the native import timer retired. Never rerun the old supplemental cutover script.

The timestamped report and verification evidence are under `output/ooru-meeting-audit`. `verify_native_meeting_preservation.py` compares original master/intake/history rows and original AWE records without changing them. Fictional tests are UUID tracked and removed by `cleanup_native_meeting_fixtures.py` after evidence is saved.

Open https://g2p-register.wverve.in/en or https://g2p.wverve.in/registration/mbr. The existing registry entry points now route to the integrated MBR workflow. It uses the existing staff Keycloak realm, portal sessions and native PostgreSQL registry. Newly approved households and their individuals are visible in the native registry, too.

## Demo access

| Account | Assigned role |
| --- | --- |
| aarin@gmail.com | Registration Officer |
| abuchi@gmail.com | Field Agent |
| abutu@gmail.com | Level 1 Approver |
| adaku@gmail.com | Level 2 Approver |
| admin@openg2p.org | Administrator |

Run `Show-MBRDemoCredentials.ps1` from this directory to view the generated passwords. They are stored only in `/opt/openg2p-lab/registration/mbr-demo-credentials.json`, mode 0600. Deployment preserves passwords on reruns. Each account has exactly one dedicated MBR realm role. The administrator cannot approve, return or reject records. No public role-switching authentication shortcut is provided.

## Workflow and persistence

- Draft → Pending Stage 1 → Pending Stage 2 → Approved / Active.
- Both reviewers may return a pending record for correction or reject it permanently. Reasons are mandatory. Returned records are editable by their submitting officer; permanent rejections are locked.
- Each stage requires a different identity. A creator cannot approve their own submission. Every write checks role, ownership, state and version on the server.
- New household IDs use `HH-` plus ten numeric digits; submission references use `YYYYMMMDD-XXXXXX`. Existing native household IDs are preserved.
- The workflow tables are `g2p_mbr_submissions`, `g2p_mbr_events` and `g2p_mbr_master_data` in the existing `register` database. Native household/member writes and final approval commit in one PostgreSQL transaction. Removing a member inactivates the native member rather than deleting it.
- Post-approval edits keep an old/new snapshot and master revision. A changed master prevents final approval and requires correction/resubmission. Native fields outside this workspace's mapping remain intact.
- Duplicate comparisons inspect pending MBR intakes and active native households. Exact NIN matches score 100%; otherwise scores combine normalized fuzzy head name (65%), age (20%) and sex (15%). The display threshold is 65%. Scores support human review and do not automatically reject a household.
- The field simulator stores unsynced synthetic households on the device, scoped to the signed-in identity. Batch sync is atomic and keyed by actor plus client-generated ID, so retries do not create duplicate submissions. Canceling an offline edit preserves the original queued household. The simulator is not a replacement for the existing Android/ODK offline client.

## Existing data and scope

The workspace reads the existing active native Master Registry. Historical IDs are retained. Legacy survey attributes absent from native tables are shown as not recorded, rather than being invented. Analytics use this same active registry, with denominators shown for NIN and bank coverage.

The historical migration is complete: 30 native intake records and two native change requests now share the MBR queue with new records. Their original UUIDs, application references, authors, timestamps, source statuses, target IDs and native payloads were retained. All 37 associated AWE requests, 71 tasks, 69 decisions and 214 events were archived losslessly. The 283 decision/event entries appear in the same records' approval histories. Five earlier rejected requests belong to subsequently approved/resubmitted intakes; they remain earlier attempts on those intakes rather than becoming duplicate or rejected current records. All 32 current source records were already approved at cutover; migration did not approve them again or replay their effects.

The full native source archive contains 8,284 rows, including source configuration, section data, native version history and duplicate evidence, with a SHA-256 checksum per row. Original native source and AWE rows were retained. Reconciliation against the recovery point verified that the 90 existing household records and 219 existing individual records were unchanged. Old values absent from historical change-request sources are explicitly marked unavailable; current values are not presented as historical old values.

The MBR workflow is the decision owner for registry artifacts. Database guards block old native mutations, AWE decisions, cancellations and reassignment for migrated registry requests, preventing parallel approval paths. New MBR decisions retain their own event history and atomically mirror relevant native intake/change-request state. Legacy-schema pending changes retain their actual pre-change snapshot, original target, first-stage reviewer and task assignment; Stage 2 does not restart at Stage 1. New decisions enforce creator/reviewer separation even when historical decisions used a more permissive policy. Historical decisions are not rewritten to satisfy the new policy.

Legacy intake and change-request detail links, and AWE request/task links for registry artifacts, resolve to the corresponding MBR record. Login preserves that destination. The original native registry/configuration view can be opened deliberately with `native_view=1`; migrated mutation guards still apply. Non-registry AWE workflows, including programme/payment approvals, retain their existing owner and are not converted into household approvals.

The established `admin`, `nsipa-demo-intake`, `nsipa-demo-reviewer-one` and `nsipa-demo-reviewer-two` identities received corresponding MBR roles without password changes. Unique original usernames, IDs and display names are mapped to their canonical identities; ambiguous names are not merged. This preserves ownership without transferring historical records to newly created demo users. The five requested demo accounts continue to work with their existing generated passwords.

New native/ODK intake and native change-request artifacts are reconciled into the same workflow by `iqs-mbr-native-import.timer`, normally within 60 seconds. The old AWE decision path is blocked immediately for registry artifacts, including artifacts waiting to be imported. No-op importer runs do not lock or rewrite source tables. Inspect `systemctl status iqs-mbr-native-import.timer` and `journalctl -u iqs-mbr-native-import.service` for import status. The importer refuses unexpected source drift, unsupported stages or identity collisions instead of silently merging records.

## Validation

`test_mbr_workflow.py` performs 35 checks in a disposable PostgreSQL schema, including stage separation, ownership, required reasons, stale writes, native promotion, change conflicts, duplicate detection, offline retry safety, permanent locking, batch rollback and admin-only analytics. It drops only its generated test schema on exit.

`pbms-react/test-mbr-ui.cjs` verifies all five real SSO logins, direct KPI navigation, member capture and draft saving, both approval stages, UUID masking/reveal, duplicate tabs, rejection-modal validation, admin restrictions, offline simulator access and 390px layout. It writes results and screenshots to `../output/mbr-verification`. `cleanup_mbr_ui_test.py` removes only the recorded generated test IDs and verifies the exact synthetic address before removing a test master.

`test_mbr_migration.py` passed 25 additional checks against restored copies of both databases. These verify ID/reference/author/time preservation, archive counts, source/master hashes, idempotent reruns, rejection of old mutation paths, preserved Stage 2 assignments and first-stage decisions, one-time native change application and approval retry protection. Its transition fixture is created only in databases named `mbr_rehearsal_*`.

`pbms-react/test-mbr-migration-ui.cjs` passed 24 read-only live checks covering historical records, all prior attempts, chronological history, old request/task links, native change links, login return destinations, missing historical old-value labels, approved-list filtering and mobile layout. `verify_mbr_migration.py` writes the final read-only database reconciliation to `../output/mbr-migration-verification/database-reconciliation.json`.

Build with `node build.cjs` in `persona-ui`, run the integration checks in the existing WSL registration virtual environment, then run `deploy-mbr-workflow.py` there. Deployment syntax-checks sources, backs up changed runtime files, preserves current live portal fixes, restarts the existing service and checks readiness. A failed deployment restores the changed files automatically. Backups and their restoration manifests are under `/opt/openg2p-lab/registration/mbr-backups/`. The additive workflow tables and seeded SSO accounts are retained when restoring application files; do not drop them to roll back a UI change.

## Migration recovery and maintenance

Full custom-format PostgreSQL recovery dumps and their restore manifests are under `/opt/openg2p-lab/registration/migration-backups/`, mode 0600. Dump/restore uses the PostgreSQL 16 tools in the existing database pod, matching the server version. The rehearsal databases are restored copies, not production schemas. Cutover manifests, routing-file backups, identity grants and reconciliation reports are under `/opt/openg2p-lab/registration/mbr-integration-backups/`. The successful routing cutover manifest is `20261112-210355/manifest.json`; its recovery-point manifest is `snapshot.json` in that directory.

`deploy-mbr-integration.py` performs the backup, ships adapters, resolves original actor identities, runs the guarded import, tests the existing registry entry point and installs the import timer. Import is idempotent: existing workflows and source history entries are linked by stable native IDs and source-event keys. A failed routing step restores changed routing/application files while retaining imported history and safe ownership guards. Restoring routing alone must not re-enable the old approval engine. A full rollback requires stopping both workflow writers, reconciling any post-cutover decisions and using the matching register/AWE recovery point together; never drop history tables or replay approvals as a rollback shortcut.
