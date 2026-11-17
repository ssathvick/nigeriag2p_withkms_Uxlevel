# OpenG2P and knowledge analytics

Installed in the current local synthetic sandbox on 7 October 2026.

## Access

- Native workspace: https://nigeriag2p.com/registration/analytics
- Superset: https://superset.nigeriag2p.com/superset/dashboard/nigeria-platform-analytics/
- Knowledge library: https://nigeriag2p.com/registration/knowledge

Staff sign in is required for analytics. Registration officers, verification officers, programme supervisors and existing intake reviewers can see the native aggregate workspace. CSV export requires a supervisor or intake reviewer. This inherits the existing sandbox-wide staff scope. Programme and state selectors are analysis filters, not authorization boundaries. Production programme or geographic access assignments are not yet implemented. Superset keeps its existing permissions; configuration does not grant Public or staff users additional Superset roles.

## What is implemented

The native page reads intake profiles, member entries, applications, backlog, synchronization exceptions, status counts and state counts. Its programme filter selects profiles with an application to the selected programme. Dates do not filter current operational status.

Dedicated read-only PostgreSQL identities collect modern registry counts and change requests, PBMS programme and beneficiary-list processing status, AWE approval status and completed-request turnaround, and Bridge instruction and bank-dispatch status. These backend aggregates have global local-backend scope and do not inherit intake filters. They are not added to intake counts because the sources overlap.

Knowledge governance counts live published payloads independently of editorial status. A published article edited into a draft still has live guidance. Review duration pairs a submission with the next review or return for that article version and reports median and 90th percentile hours. Current editorial counts are snapshots; dates filter review decisions and usage.

The library records nonempty searches and result counts, guide opens and helpfulness votes. Tracking does not store query text, names, beneficiary payloads, tokens or bank details. Votes are limited to one per session, article and published version per UTC day. Opens are counted once per rendered article per page load. They are not unique readers. Contextual help panels on other domains are not instrumented. One guide open and helpful vote were recorded during live browser verification; these are sandbox verification activity.

Usage POSTs use the application's existing CSRF check. UUIDs deduplicate retries. Published version validation rejects stale or private article events. Sessions are represented in the raw usage table by a digest of the random session ID. The collector deletes raw usage older than 90 days and daily aggregates and operational snapshots older than 366 days. Collection starts at installation; no historic usage is fabricated.

## Reporting pipeline

`platform_analytics.py` installs SQLite event, aggregate, snapshot and source-cache tables in the existing intake database. `analytics_sources.py` reads fixed aggregate queries using read-only identities, updates per-source caches, captures the daily intake snapshot and publishes anonymized aggregates to the separate PostgreSQL `g2p_analytics` database.

Reporting tables are `aggregate_metrics`, `knowledge_governance` and `knowledge_daily_usage`. Superset has a read-only connection, three datasets and three table charts on the analytics dashboard. DML, file uploads, CTAS, CVAS and SQL Lab exposure are disabled for that connection. Its source dataset derives stale status from the last refresh age as well as refresh failures. Summaries show UTC timestamps. Knowledge usage daily buckets use UTC.

The `iqs-analytics.timer` runs after boot and every 15 minutes. Native intake and knowledge metrics are read on each dashboard request. Backend and Superset aggregates refresh on the schedule. A failed backend refresh preserves the previous valid summary and marks the source failed. The native page warns when a source is older than 30 minutes. A reporting transaction replaces all three reporting tables atomically. A failed collector exits nonzero so systemd records failure.

## What is not yet measured

Confirmed bank settlement and financial reconciliation metrics require validated settlement evidence and currency-aware mapping. Bridge acceptance and PBMS `complete` process status are never described as settled payments. Guidance-to-task causal attribution, contextual-help usage, national LGA mapping, formal content-review due dates, geographic authorization policies and automatic business alerts are not part of this release. The current dataset provides actual sandbox status summaries, not production impact claims.

## Operate and verify

From PowerShell, use WSL with the lab's existing virtual environment:

```powershell
wsl -d Ubuntu-22.04 -u root -- systemctl status iqs-analytics.timer --no-pager
wsl -d Ubuntu-22.04 -u root -- systemctl start iqs-analytics.service
wsl -d Ubuntu-22.04 -u root -- journalctl -u iqs-analytics.service --since today --no-pager
wsl -d Ubuntu-22.04 -u root -- /opt/openg2p-lab/registration-venv/bin/python /mnt/h/Nigeria_Mosip/codex/openg2p-lab/verify-analytics-live.py
```

Credentials are stored only in `/opt/openg2p-lab/registration/analytics-connections.json`, mode 0600. Do not print or export that file. Database identity provisioning uses administrative credentials only at installation; collection and Superset use their dedicated identities. Source service ClusterIPs are stored in this file and must be reprovisioned if services are recreated with new IPs. Re-run `setup-analytics-database.py` within WSL after such a change, then re-run `install-superset-analytics.py`.

The read-only collector may report a schema or connection failure after an upstream upgrade. Validate the changed schema and update the fixed queries; never convert a failed query into a zero count. Operational code and publishing permissions are unaffected by reporting failures. A failed search-event recording caused by the rate limit does not block the knowledge library.

## Installation and recovery

`install-analytics.py` makes a private SQLite backup and saves original application files under `registration/analytics-backups` before deployment. It installs additive schemas, read-only database identities and the scheduled collector. `install-superset-analytics.py` transfers its connection privately to the existing Superset container and removes the temporary connection file in a finally block. Configuration is idempotent by database name, dataset name, chart name and dashboard slug. Superset failures are logged privately without returning connection strings.

`install-analytics-navigation.py` backs up and deploys the rebuilt site, shell and workspace assets so the service catalogue links to the native Analytics workspace. Future rebuilds must retain the catalogue change in `persona-ui/src/catalogue.js`.

For application rollback, stop `iqs-analytics.timer` and `iqs-registration.service`, then restore the files listed in the corresponding private backup manifest and restart registration. Do not restore the old SQLite database blindly after users have continued working; the analytics tables are additive and can remain dormant. The database snapshot is for recovery only after assessing subsequent writes. Reporting roles and datasets can remain unused without changing the operational data. Superset metadata configuration adds a new analytics dashboard and leaves other dashboards and permissions unchanged.

## Validation evidence

Isolated tests cover anonymous and beneficiary denial, assigned staff access, supervisor-only export, published guidance while a revision is drafted, CSRF, stale versions, UUID retries, search text exclusion, duplicate daily feedback, zero-result and helpfulness rates, privacy of output, snapshots, invalid filters and review episode duration. Existing knowledge and staff workspace tests also pass.

Live verification reconciles native totals with the installed database, confirms all four backend refreshes succeeded, verifies source identities are non-superuser and read-only, checks the Superset reader cannot insert into the reporting tables, and confirms the live API rejects anonymous analytics access. All three Superset chart queries were executed successfully. Browser verification checks the rendered dashboard and the live library feedback confirmation.


## Geographic reporting refresh repair — 17 November 2026

The scheduled collector failed because its geography aggregate views depended on the
native `ng2p_record_geography` invoker-security view. The read-only reporting identity
could not read the underlying geography catalogue through that invoker boundary.

`geographic_reporting.py` now provisions a no-argument, fixed-SQL aggregate function,
`nsipa_reporting.geography_record_counts()`, used by the three geography reporting views.
It returns only record type, zone/state names and counts, with a locked `pg_catalog`
search path. PUBLIC execution is revoked; only the existing reporting reader receives
execution permission. Native invoker view settings, row policies, record identifiers,
transactional data and application roles are unchanged. No base-table grants were added.

`provision-service-reporting.py` creates this function before geography reporting views,
and the canonical/live `service_reporting.py` geography queries use it. Existing source
and Superset readers remain read-only and non-superuser. Geography stays restricted to
the existing supervisor/intake-reviewer reporting scope; it is still excluded from the
broader Superset aggregate export. Counts are registry records, not benefit recipients.

Verification: all three geography metrics reconcile with the source views, cached
geography data refreshed without error, all 15 collector sources report healthy, and
the existing 15-minute timer remains active. Anonymous analytics/geography requests
remain denied. Programme map permissions/totals and the existing reconciled simulator
payment report passed read-only regression checks. No new payment was dispatched.

Private pre-change view/source and security metadata backups are under
`registration/analytics-backups/geographic-refresh-*`; never publish those backups.
Sanitized local verification is in `outputs/geographic-reporting-repair/verification.json`.


## Reporting timer startup persistence — 17 November 2026

The existing iqs-analytics.timer is now startup-enabled as well as active on the original
host. Its schedule remains OnBootSec=2min and OnUnitActiveSec=15min, with Persistent=true.
The startup source helper enables this existing timer and the Windows boot helper checks
its activity/enablement. The one-minute service recovery loop excludes reporting timers
so explicit Portal Control stop actions remain respected. See docs/current/STARTUP-AND-REPORTING.md.
The Windows boot task was observed running after today's restart. No second full Windows
reboot was performed after the reporting timer enablement change; verify this final step
on a destination before claiming its own cold-boot acceptance.
