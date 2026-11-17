# Programme geographic analytics — 16 November 2026

Open **PBMS → Programme analytics**, or choose **Programme analytics** from the existing Programme approval flow. Select a programme and one enrolment/disbursement cycle. The map reuses the main-panel Nigeria boundaries for all 36 states plus FCT. Select a state with the map, keyboard, dropdown or state table. Disbursement cycles support included-beneficiary and calculated-NGN measures.

## Access and data meaning

**Programme Admin, Payment, Finance, Audit and CEO** can read analytics within their existing programme permissions. The server checks both programme membership and cycle ownership. It returns aggregate counts/amounts, without beneficiary IDs, household coordinates or individual record details. No role, password or bank permission changes are required.

Coverage uses included beneficiary snapshots for **approval-flow programmes** and the selected cycle. Corrections and exclusions are preserved. A registry entry can be a household, farmer or student; household counts do not count individual household members. Pending/failed calculations are not presented as completed coverage. Existing legacy programmes without these native list snapshots are not included in the selector.

Recognized state names, local NG01–NG37 codes and ISO-style state abbreviations are crosswalked to the existing boundaries; for example PL maps to Plateau. Missing/unrecognized locations remain in the **Unmapped location** total. No state is guessed. This feature supports state/FCT aggregates; a reliable PBMS LGA boundary or GPS-point connection is not claimed.

**Submitted for payment** is a submission count, not confirmed settlement. The linked payment report remains the authority for dispatch/reconciliation. The map does not calculate eligibility, approve a list or initiate payment.

## Install/update

Use the existing [installation guide](INSTALLATION.md). The native addon includes `nsipa_approval/analytics.py`, imported by `__init__.py`. The existing `release/install_pbms.py` plan/apply installer discovers these source files, backs up the destination, and persists them through its declared ConfigMap mount. No new fields/tables or Python packages are added by analytics.

After staging the source for destination hosts/paths, inspect then apply the existing addon helper:

```bash
sudo python3 "$SOURCE/release/install_pbms.py"
sudo python3 "$SOURCE/release/install_pbms.py" --apply
cd "$SOURCE/pbms-react"
npm ci
npm run build
```

Publish `dist` through the existing atomic static release symlink. Retain the established Nginx and payment-worker configuration. New frontend files are `src/programme-analytics.jsx`, `src/programme-analytics.css` and the bundled `src/nigeria-states.json`; navigation is added in `main.jsx` and the approval-flow heading. The main-panel map is unchanged.

Boundary attribution: geoBoundaries / GRID3 2022, CC BY 4.0, source commit 9469f09. The bundled file is copied from the existing `registration-ui/nigeria-states.geojson`; no household point data is included.

## Verification and recovery

On the original lab, totals reconciled for every available programme/cycle. Five actual-role browser sessions passed programme/cycle filtering, state selection, both measures, mobile layout and all 37 map shapes. Unassigned-programme access and a cycle belonging to another programme were denied. Missing/unknown-state handling and all 37 boundary crosswalk IDs were checked. Analytics reads preserved approval, revision and payment state.

The browser programme creation → enrolment → disbursement → Payment review submission → Finance/Audit/CEO → XLS export regression passed. The existing reconciled payment API and linked report/download checks passed; analytics dispatched no new payment. The synthetic regression programme was paused. See the [sanitized verification summary](../../source-snapshots/2026-11-16-programme-analytics/verification-summary.json).

The included backend/browser test sources depend on the existing synthetic connected-payment fixture. Run fixture-based checks only in a verified isolated lab. Supply browser/backend role credentials using the private `PBMS_APPROVAL_ACCOUNTS_FILE` environment path; never commit its contents. `PBMS_EMPTY_ANALYTICS_PROGRAMME` optionally identifies a destination empty-cycle fixture for its browser empty-state check.

For rollback, restore the prior static release and matching addon ConfigMap/deployment from the private recovery point. Do not edit beneficiary IDs, approvals or payment records to remove analytics. The addition creates no analytics data store requiring a database rollback.

The separate [main-panel geographic reporting refresh repair](GEOGRAPHIC-REPORTING-FIX.md) fixes its scheduled aggregate collector. Programme-list map scopes, snapshots, filters and payment actions are unchanged by that repair.
