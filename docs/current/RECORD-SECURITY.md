# Master Registry ownership and independent authorization

Implemented in the native Registry API, PostgreSQL and AWE, with matching Registry UI. The original logo and retained application sections are unchanged.

## Access matrix

| Record state | Creating field agent | Other field agents | Level 1 | Level 2 | MBR Officer | MBR Admin |
|---|---|---|---|---|---|---|
| Draft | Read/edit | No | No | No | No | All |
| Awaiting Level 1 | Read | No | Review | No | No | All |
| Awaiting Level 2 | No | No | No | Review | No | All |
| Revalidation requested at either level | Read/edit/resubmit | No | No | No | No | All |
| Approved at both levels | No | No | No | No | Read published master | All |
| Permanently rejected at either level | No | No | No | No | No | Rejected archive |

Native client roles: `Registry Field Agent`, `Registry First Reviewer`, `Registry Second Reviewer`, `Registry Officer`, `Registry Administrator`. Assign exactly one Registry persona per account. Conflicting personas fail closed. Officer is read-only and has no submission/review/write permissions. Reviewers must use their assigned AWE task; Admin cannot substitute for either independent reviewer.

See [FIELD-ASSISTANT-FLOW.md](FIELD-ASSISTANT-FLOW.md) for five-field-assistant setup and the complete homepage-to-publication walkthrough, including the mobile QR stopping point.

## Daily use

1. Field agent signs into the Master Registry block, captures a household and members, saves a draft, then submits. The creator sees only their own work.
2. Level 1 opens Approvals. **Approve** removes the record from creator and Level 1 and sends it to Level 2.
3. Level 2 approves. Its queue loses the record; the approved household/members become visible to Officer after the native publication worker finishes.
4. At either review level choose **Revalidate — return to field agent**, with a reason, to return the record to its creator. The creator corrects and resubmits, restarting independent Level 1 review.
5. **Reject permanently**, with a reason, archives the record for Admin only. Admin opens Form submissions → **Rejected archive**. Revalidation and permanent rejection are separate actions.

Five dedicated demonstration accounts are provisioned as `field-agent-01@nsipa.example.invalid` through `field-agent-05@nsipa.example.invalid`. These are login identifiers, not deliverable mailboxes. Passwords are generated privately and never committed. Existing Abuchi remains an additional field account. Existing reviewer, Officer and Admin passwords are preserved.

## Enforcement

- IAM verifies the JWT before request scope is derived. Ownership is the verified Keycloak subject, never `created_by`, enumerator name, URL parameters or browser storage.
- SQLAlchemy applies transaction-local role/subject settings and switches non-admin HTTP transactions to a non-owner `NOBYPASSRLS` role. ContextVars and `SET LOCAL` isolate concurrent requests and pooled connections.
- Row policies cover 69 record-bearing tables, including master/intake sections, document links, history, comments, deduplication candidates and archives. The geography view uses invoker security. Private provenance tables are inaccessible to scoped roles.
- Native service workers and validated signed callbacks retain service authority. Review transitions update access synchronously after AWE accepts the assigned decision. Event ordering/current-attempt checks prevent delayed callbacks from restoring old access.
- Record caches are disabled for scoped API requests; responses are private/no-store. Direct IDs, search/count endpoints, completed task histories and direct AWE reads share the scope rules.
- Registry request creation requires a fresh internal HMAC from the native Registry helper. The key lives in Kubernetes Secret `nsipa-record-security`, never frontend code. Direct browser AWE requests cannot choose a different approval policy/callback to bypass review.
- Deprecated integrated `/registration/mbr` reads redirect to the native Registry; writes return 410. They cannot expose an older unscoped record store. A secondary guard also restricts legacy handling to the verified Registry Admin directory if the redirect is removed in a future migration.

## Offline capture

Use the authenticated **Offline field capture** setup screen for each field user. Setup binds the verified staff subject to Central's actual App User ID in the private synchronization configuration. The worker reads Central's `submitterId`, not editable XML metadata. Only the pinned `nsipa-odk-registry-sync` service account may present an owner header; the native API validates that owner against the private field directory. Unknown submitters are quarantined for explicit reconciliation. The same two reviews and publication rules apply to offline records; the synchronization worker never approves them.

Do not infer historical ownership from display names. Legacy records without verifiable current staff-subject provenance remain Admin-only. Their data is preserved; adding provenance requires an audited mapping backed by authenticated source evidence. No legacy ownership is silently guessed or reassigned.

## Install or restore this security layer

Run after the base native Registry, AWE, IAM persona setup and ODK service client are installed. Use the release's matching native module versions in `original/`. The deployment scripts target namespace `nigeria` and the established private `/opt/openg2p-lab` layout; adjust paths/service names for another installation before executing. They require administrative Kubernetes/DB access and the private Keycloak admin credential file.

From the lab source directory, using the registration virtual environment:

```bash
python provision_record_security_agents.py
python record-security/build_policies.py
python record-security/prepare.py
python record-security/prepare_awe.py
python deploy_record_security.py
python deploy_awe_record_security.py
python deploy_native_offline_setup.py
```

Install the updated `client-concerns/odk_sync_worker.py` in the private ODK-sync runtime. Preserve `config.json`, receipts and ledger; do not replace them with source examples. Reopen authenticated Collect setup for each existing field App User to establish trusted ownership. Re-run `deploy_awe_record_security.py` after field/admin membership changes to refresh the private identity directories. Do not grant human accounts the integration service credential or the scoped database role.

Build `registry-ui-source/Dockerfile.native`, then deploy the image with `deploy_meeting_native_ui.py IMAGE`. Both API ConfigMaps must remain mounted at their actual imported site-packages paths. A UI build alone does not install enforcement.

`deploy_record_security.py` creates private PostgreSQL dumps of Registry/AWE/IAM and deployment backups before applying the additive schema. AWE deployment also captures its deployment backup. Back up the security schema, identity mappings, signing Secret, ODK state and accounts during operational migration. Git contains no passwords, private exports, production records or recovery dumps.

## Validation

Live authenticated tests cover ownership/direct IDs, creator-name spoofing, both approval handoffs, both return/reject paths, approved-only Officer access, scoped counts and completed queues. Extended tests exercise all five agents pairwise, concurrent pooled requests, cross-account writes, forged owner headers and authenticated offline ingestion. The signed suite repeats the workflow with internal request authorization enabled. `pbms-react/verify-record-security.cjs` checks nine isolated browser sessions, persona notices and the Admin archive filter in headless Edge; it does not attach a debugger to the user's Chrome.

Tests create UUID-tracked fictional fixtures. Keep their private evidence outside public Git and remove only the tracked fixture IDs after validation. Test helpers need private local credentials and are not a generic production load test.
