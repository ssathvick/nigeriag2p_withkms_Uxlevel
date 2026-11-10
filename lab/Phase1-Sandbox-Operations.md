# Phase 1 sandbox operations

Updated on 12 October 2026. This release adds testable demonstration workflows;
it does not certify completion of the NSIPA Build Phase.

## Open the release

- Staff module workspace: https://nigeriag2p.com/registration/phase1
- Device delivery queue: https://nigeriag2p.com/registration/phase1/field
- Four-language portal preview: https://nigeriag2p.com/registration/phase1/portal
- Staff readiness evidence: https://nigeriag2p.com/registration/phase1/readiness
- Staff CMS: https://nigeriag2p.com/registration/phase1/cms
- Citizen grievances: https://nigeriag2p.com/registration/phase1/grievances

Use the existing staff supervisor or intake-reviewer account. No new account,
role grant or external API exposure is needed. The public launcher links to the
workspace and portal preview.

## Demonstrate the new workflows

1. Create a grievance for a supplied DEMO-HH reference. Select one of six
   simulated intake channels. Acknowledge, escalate and resolve the case.
   Version checks reject stale actions. Response and resolution deadlines are
   48 hours and 14 days from creation. A minute timer escalates overdue cases.
2. Train and certify a fictional agent. Each of six agents is assigned to a
   demonstration household territory. Revoked/unqualified agents cannot add
   delivery proof. These records are separate from native partner management.
3. Open field delivery online and wait for "Offline page available". Save proof
   to the browser IndexedDB queue. Reconnect, then synchronise. Successful
   retries are idempotent; conflicts remain visible. A second delivery for the
   same demonstration household is rejected.
4. Switch English, Hausa, Yoruba and Igbo in the public portal. Locations and
   content are fictional examples. Author, independently review and publish
   a revision through the staff CMS. The old published version remains available
   during review. Translation approval and full self-service integration remain pending.
5. Use existing household/registry, PBMS, partner simulation, partner management
   and KMS links in the workspace to review the other modules.

No real biometric check, GPS reading, message or payment is performed by the
new demonstration module. Supplied coordinates and accuracy values are test
inputs. A 48-hour offline result requires an actual duration test on devices.

## Repeat automated verification

Run in PowerShell:

```powershell
wsl -d Ubuntu-22.04 -u root -- /opt/openg2p-lab/registration-venv/bin/python /mnt/h/Nigeria_Mosip/codex/openg2p-lab/run-phase1-checks.py
wsl -d Ubuntu-22.04 -u root -- /opt/openg2p-lab/registration-venv/bin/python /mnt/h/Nigeria_Mosip/codex/openg2p-lab/verify-phase1-native.py
```

The first runner tests temporary isolated databases; it does not reset live
records. Actual logs and JSON summaries are saved in `phase1-evidence/`.
The second performs read-only native signed Bridge-to-SPAR resolution and
backend inventory checks. Upstream logs, tokens and credentials are not
included in its public result summary.

Verified: 85 test executions across seven suites, including inherited cases that
repeat across some suites. A native enrolled synthetic household calculated
NGN 25,000, used signed SPAR account update and resolution, received its fictional
local Example Bank credit, and reconciled through native Bridge. Nine fictional
instructions reconciled with zero exception entries in the measured fixture.
Initial clearing-route tests remain in history. No live rails were used.
Native bank replay and duplicate MT940 upload/replay preserve financial counts.
Fictional CCT conditionality requires at least 80 percent attendance, independent
verification and a third officer's release or hold decision. Below-threshold
evidence cannot be released. It does not dispatch funds or enforce native PBMS
conditions. Approved CCT policy and native integration remain separate gates.
Saved statement callback failure/retry was verified without ledger or balance
changes. Initial pending bank statement requests were retried through native code;
empty requests are NOT_APPLICABLE rather than counted as successes. Statement
dates now derive from each new request, and negative/non-finite amounts are
rejected. A million native instruction models validated in 1.706 seconds without
dispatch; that check does not establish a million settled payments.
Six concurrent native PBMS reads passed; full concurrent workflows are pending.
The separate demo agent module handled 50,006 records; its report p95 was 0.0143s.
The separate native registry SQL benchmark is recorded in capacity-native-registry.json;
it does not establish full API or deduplication performance. Browser checks confirmed
grievance resolution, certification and delivery sync; offline cache preparation
was visible. Formal NSIPA UAT remains Not run.

## Remaining readiness gates

- Full native conditionality, jurisdiction and failure/recovery case coverage;
  connect field delivery proofs to native payment records.
- NIN/BVN and biometric de-duplication remain simulated; measure production
  criteria only against authorised identity systems and labelled cohorts.
- Full registry API/deduplication, 1M native payment batch, native 50,000-agent
  workload and six concurrent full programme workflows. The separate SQL and
  demo-agent benchmarks do not substitute for application-wide acceptance.
- 48-hour real-device offline test, location and biometric performance tests.
- Full public self-service integration, independent language review,
  WCAG 2.1 AA audit, performance measurements and security/penetration review.
- Approved hosting/compliance/availability evidence and client UAT sign-off.
- Actual six-LGA CCT pilot, independent evaluation and joint acceptance are
  production-phase dependencies; demo location rows do not replace that pilot.

## Deployment and recovery

Runtime module/data: `/opt/openg2p-lab/registration/phase1_sandbox.py` and
`phase1-sandbox.sqlite`. Existing intake and financial databases are not
rewritten by this module. Private deployment snapshots retain touched files,
SQLite backups and unit manifests in `registration/phase1-backups/`.

`iqs-phase1.timer` invokes `phase1-worker.py` every minute. Review health with
`systemctl is-active iqs-registration.service iqs-phase1.timer`. Deployment uses
`install-phase1-sandbox.py` with an inspected runtime hash guard and automatic
file rollback if verification fails. Do not indiscriminately restore a database
over newer test work. Back up the new SQLite database with SQLite's backup API,
not by copying an active WAL database file alone.

Browser proof remains on the specific device, including after session expiry.
Sign in again before sync. Browser clearing/private browsing can remove the
local queue; retain UAT evidence externally before clearing it.

## Run the actual offline duration case

Record device, OS, browser, build, tester and UTC disconnect time. Disable network
connectivity, capture fictional proof, close and reopen the browser, and remain
disconnected for at least 48 hours. Record UTC reconnect time and sync receipt.
Retry and verify exactly one delivery. Do not simulate elapsed time by changing
the clock. Report queue loss or restart failure. Mock matches and supplied
accuracy values do not prove biometric or GPS performance.

## Native fixes and safe verification

Native compatibility fixes are pinned in named Kubernetes ConfigMaps for strict
mapping, stable statement receipts, durable entitlement counters, statement and
bank replay guards, ledger-derived statements and the bank API Redis dependency.
Private pre-change deployment manifests are retained in phase1-bank-backups.
Helm upgrades must retain these mounts or incorporate equivalent upstream fixes.
No new signing keys, accounts or role grants were introduced.

Use verify-native-household-payment.py, test-native-bank-replay.py and
check-public-readiness.py for retests. publish-readiness-evidence.py copies only
sanitized summaries to the staff-only readiness view. Do not rerun initial payment
approval or seed scripts as verification; they create fictional test cycles.
Old failed statement requests and unused fixture envelopes remain test history.
Native diagnostics, credentials and rollback manifests are excluded from the
client pack. The canonical source is openg2p-lab; the GitHub snapshot is older.

The minute worker now collects origin and public health observations. Missing
expected observations count as unsuccessful in the displayed calculation. An
agreed observation window is required before claiming the 99.5 percent SLA.
Backup restoration, failure recovery and an independent penetration assessment
are still acceptance gates; routine file rollback is not a restore-drill pass.
An isolated restore of both SQLite databases passed integrity, table-count and
index checks. Whole-stack PostgreSQL recovery and agreed RPO/RTO remain pending.
