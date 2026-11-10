# Nigeria G2P partner simulation

Open https://nigeriag2p.com/registration/simulation and sign in as a programme
supervisor or intake reviewer. Select a scenario and click **Run scenario**.
The journey page shows each local partner exchange. Refresh after approximately
10–20 seconds to see settlement; delayed settlement waits approximately two
minutes plus the worker interval.

## Implemented scope

This is an isolated demonstration inside the existing platform, using its staff
login, navigation and CSRF protection. It provides local identity, social register,
programme, treasury, account validation, payment, notification, grievance and
reconciliation responses. It does not contact Nigerian agencies, send messages,
or issue payments. The contracts are simulation specifications, not official
agency specifications. The complete journey is orchestrated by the simulator;
it does not yet exercise the real PBMS/AWE/Bridge execution path.

Synthetic records remain in `partner-simulation.sqlite`, separate from intake,
registry and payment databases. Native OpenG2P operational totals exclude them.
The analytics page links to the separate simulation dashboard. Existing knowledge
library measurement continues to track actual searches, guide opens and feedback;
simulation events are not fabricated as knowledge usage.

## Scenarios

| Scenario | Expected result |
|---|---|
| Successful transfer | Accepted, then callback and matched settlement |
| Identity mismatch | Stops before eligibility and payment; grievance opened |
| Ineligible household | Stops at social-register eligibility; grievance opened |
| Invalid account | Stops before funding/payment; grievance opened |
| Insufficient funds | Treasury rejects funding; no payment |
| Payment failure | Bank rejects instruction; no settlement |
| Delayed settlement | Accepted remains pending for two minutes |
| Reconciliation mismatch | Completion callback followed by amount discrepancy |
| Reversal | Reversed outcome; excluded from settled total |

Every run uses a fictional four-member Kano household and a NGN 25,000 benefit.
Amounts are integer kobo (2,500,000). Request UUIDs deduplicate runs; reusing a key
for another scenario returns 409. Callback UUIDs deduplicate completion events;
conflicting reuse or invalid state transitions return 409. SQLite transactions
serialize state changes and prevent duplicate worker settlements.

## API and schemas

Download `/registration/api/simulation/schema` after staff login. The checked-in
`simulation-openapi.json` contains OpenAPI 3.1 request and response contracts.
POST bodies use `application/x-www-form-urlencoded` with the existing session's
`csrf` token. APIs use staff cookies; machine-to-machine partner authentication
has not been introduced in this release.

| Route | Purpose |
|---|---|
| GET `/registration/api/simulation/report` | All current runs, outcome counts, matched settled amount |
| POST `/registration/api/simulation/runs` | `scenario`, UUID `request_key`, `csrf` |
| POST `/registration/api/simulation/partners/{service}` | Standalone response for selected `scenario` |
| POST `/registration/api/simulation/callback` | UUID `run_id`, UUID `event_id`, `status`, `csrf` |
| POST `/registration/api/simulation/reset` | Explicit `RESET SYNTHETIC RUNS` confirmation and CSRF |

Supported partner names: `identity`, `social-register`, `programme`, `treasury`,
`account`, `payment`, `notification`, `grievance`, `reconciliation`.
Standalone partner responses are fixed fixtures and do not create a journey.
No arbitrary real NIN, account, phone, beneficiary or callback URL is accepted.

## Analytics

The console shows journey count, outcome distribution, pending completion count,
settled count and settled amount. Only matched `settled` runs contribute to the
settled amount; mismatches, reversals, failed transfers and pending transfers do
not. Values represent synthetic results, not bank-certified settlement.
Simulation users share the sandbox's full simulation scope. The report includes
up to 1,000 runs; creation stops at that limit until reset. There is no date filter,
production geography scoping or Superset simulation dataset in this release.

## Background operation and recovery

`iqs-simulation.timer` invokes `iqs-simulation.service` every ten seconds. The
worker drains due accepted payments transactionally; a deterministic callback ID
makes restarts safe. Delays persist in the database and are processed after restart.
The oneshot service becoming inactive after a successful run is normal.

Run inside WSL Ubuntu as root:

```sh
systemctl status iqs-simulation.timer
journalctl -u iqs-simulation.service -n 40 --no-pager
systemctl start iqs-simulation.service
```

The database is `/opt/openg2p-lab/registration/partner-simulation.sqlite`, mode 0600.
Use SQLite's backup API for consistent copies while WAL is active. The installer
backs up touched application files under `simulation-backups/` and restores them
on deployment failure. It does not overwrite existing simulation data.
Reset deletes all runs, events and callbacks only in this separate database,
including runs created by other simulation staff. Download the JSON report first
if outcomes must be retained. This is a demonstration sandbox, not production
financial audit storage.

## Verification and next integration stage

Isolated tests cover all nine outcomes, permissions, CSRF, request idempotency,
callback conflicts/retries, delayed processing, settled totals, reset cascades,
page rendering and isolation from intake records. Live installation verification
retains three synthetic example runs. Platform analytics and workspace tests are
also run to check regressions.

To exercise native OpenG2P execution, the next stage is to implement adapters
against the installed PBMS, AWE and Bridge contracts, replace the selected sandbox
partner configurations and verify enrolment-to-disbursement through those systems.
That work must preserve synthetic programme separation and callback compatibility.
