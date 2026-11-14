# Connected PBMS payments — 15 November 2026

The same CEO-approved list now continues into payment processing. This update preserves existing account usernames/passwords, approved history, corrections and XLS export. It does not automatically dispatch previously approved lists.

## Staff journey

1. Programme Admin configures the programme, cash benefit, rules and monthly cycles. Enrolment processing selects registry beneficiaries; the disbursement list calculates entitlements.
2. Payment initiates review of that list. Finance, Audit and CEO approve sequentially using independent authenticated accounts. Rejection/correction/resubmission restarts the approval chain for a new revision.
3. Programme Admin opens the list's **Payments** section, selects an existing configured **Sponsor bank routing**, and saves it once per programme. One NGN digital-cash benefit is required. Routing locks after payment submission.
4. After CEO approval, Payment opens that same list and selects **Proceed to payments → Confirm and proceed**. The confirmation shows the approved revision, included beneficiary count and total. The Payment role and programme membership are checked on the server.
5. **View payment progress → Payments → View report** shows the linked envelope/batch and Bridge financial-address resolution, dispatch and reconciliation. Download the report as needed. Submission and approvals remain after refresh.

CEO approval alone does not send money. The XLS export remains available after approval. Payment does not need a separate beneficiary list or another approval chain. The existing Payments sidebar can also open the same approved list.

## Payment integrity and current limit

The Payment action validates Finance, Audit and CEO decisions against the current revision/content hash, records the actor and timestamp, and locks the list before queuing the native worker. The worker validates the same snapshot and independent approvers, carries only included beneficiaries at their approved amounts into native payment records, and never reruns eligibility or entitlement rules. Stable envelope identifiers, existing-record checks and the submission lock prevent repeat requests or completed worker replay from creating another batch. Dispatch and reconciliation are reported separately.

The installed Bridge stores declared envelope quantities as integers. Connected payments therefore require **whole NGN entitlements**. Fractional amounts are blocked before approval and payment; they are never silently rounded. Full fractional-currency support needs a separate Bridge model/database migration. This release does not perform that migration.

The red-marked sidebar entries removed are Households, Farmers, Students, Priority rules, Agencies, Warehouses & banks, States & regions, Local administrative areas, Agency benefit assignments, Bank & warehouse assignments, and Verification queue. Supporting routes, records and relationship selectors remain available to the workflow.

## Installation and recovery

Follow [INSTALLATION.md](INSTALLATION.md): update the native addon, install the version-checked payment worker extensions, update the session adapter, build the frontend and publish its static release. Preserve `PBMS_ALLOWED_ORIGINS` for destination hosts. The payment worker installer checks the upstream worker source before mutation, backs up the deployment/previous ConfigMap, and mounts the helper and two worker extensions persistently. Do not install source built against a different upstream worker version.

The repository contains no passwords or running database. Existing-host updates preserve credentials. Fresh installations provision their own accounts and secrets; cloning cannot recreate original private identities or bank settings. Configure and verify real payment connectors separately from the supplied local simulator.

If payment processing fails, inspect the linked report and worker status before retrying. Use the existing worker retry mechanism; do not clear the submission hash, edit approved amounts in PostgreSQL, create another list, or replay bank dispatch as a recovery shortcut. Restore only from the matching private deployment/ConfigMap and database recovery point after reconciling any transactions created since backup. Keep the approval/payment audit history.

For restart recovery, `release/install_service_recovery.py` can enable existing systemd portal services and a one-minute start timer. WSL also requires a Windows task to launch its distribution. The original host has a sign-in task. The administrator-only `Install-BootStartup-Admin.ps1` before-sign-in task was prepared but not installed in the non-elevated session; a full machine reboot test remains pending.

## Verification on the original lab

The actual browser journey passed programme creation, monthly cycles, enrolment, disbursement calculation, Payment submission, Finance/Audit/CEO approvals, evidence upload/download and binary XLS export. Backend checks passed rejection/correction/resubmission, independent approval, immutable verified data, denied premature/unauthorized payment and direct-state tampering.

The connected test corrected an initial NGN 2 entitlement to NGN 1 and excluded another synthetic beneficiary. The resulting same-list payment had exactly one included beneficiary, one envelope and one batch. Local simulator dispatch and reconciliation both completed. Repeated submission and completed worker replay did not create another batch. The Payment account opened/downloaded its linked report, and mobile layout checks passed. Test programmes were paused; existing legacy payment and sidebar regressions also passed.

The sanitized [verification summary](../../source-snapshots/2026-11-15-pbms-payments/verification-summary.json) contains outcomes without private account manifests, beneficiary records, original database IDs, cookies, documents or screenshots. These results do not certify real bank settlement or a fresh-machine installation. Run the destination acceptance checks against its own accounts and configured connectors.
