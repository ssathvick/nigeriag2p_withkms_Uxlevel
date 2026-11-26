# KMS and PBMS Finance sandbox release

The 26 November 2026 sandbox release added an instruction-level case register to Programme approval flow. Payment creates a case and sends it to the programme Finance queue. Finance acknowledges the same case, records or amends its outcome and obtains independent review before closure. Staff can look up the approved amount and dated statement entries by instruction. Later evidence is attached to the original closed case.

## Implementation

In the lab source, `pbms-react/finance_cases/` contains the Flask routes, register screen, Bridge views and sandbox installer. The adapter registers the routes in `pbms-react/workflow_api.py`. The queue and instruction links are in `pbms-react/src/programme-flow.jsx`. The integration uses the existing PBMS session, programme scope and configurable origin setting.

The installation script targets an existing sandbox with the PBMS adapter, registration virtual environment, Bridge, systemd service and current web release. Build the repository’s frontend in `pbms-react` with `npm ci` and `npm run build` before using the sandbox installer. It stages the bundle, installs the case service and restricted evidence views, and switches the release after its health check. Site-specific credentials are generated or supplied on the target.

The KMS source includes the staff review register, draft checks, role-aware Help and corrected content for guides 336 v2, 372 v3 and 475 v2. The [installation guide](../OORU-DOCS-HELP-INSTALL.md) covers the destination-specific documentation and Help build.

## Verification

The [source manifest](sandbox-source-20261126.json) records SHA-256 hashes of the release files with LF line endings. Its bundle hashes identify the JavaScript and CSS served by the tested sandbox. Each repository retains its own frontend baseline and deployment configuration. The sandbox bundle can be reproduced by building the repository’s Finance screen with the other frontend inputs from that sandbox release.

Four retained synthetic cases matched the original 28 recorded events, including the sent and acknowledged case references. Read-only checks with the existing Payment and Finance accounts confirmed the list 50 queue, original instruction and statement evidence. Both installed Bridge view definitions matched the supplied SQL. Each checkout also created a case in temporary storage, sent it as Payment, acknowledged and recorded the outcome as Finance, and retrieved it from the queue. The 32 KMS regression tests passed in each checkout. Both documentation builds produced 598 pages and included the corrected wording on all three guide pages and in search.

The [feedback completion report](Swift_G2P_KMS_Feedback_Completion_Response_26Nov2026.pdf) records five successful role tests. All five operational procedures still require a decision on the [Finance sign-off form](Swift_G2P_KMS_Finance_Signoff_26Nov2026.pdf).
