# OORU implementation handoff: Nigeria CCT platform

Status: engineering handoff for a synthetic sandbox, 28 October 2026. This is not a production release or authorization to process real beneficiaries or payments.

## Starting point

Use the deployed OpenG2P lab and the sources in this directory as the reference implementation. The existing registration integration connects approved synthetic household intake to the modern registry, Odoo social registry, beneficiary portal and PBMS household adapter. Programmes created through that workflow are mapped; unrelated existing programmes are not automatically migrated. Read Registration-Integration-Operations.txt for the actual workflow and its limitations. The base README's portal/PBMS compatibility warning still matters: the integration is a custom bridge, not proof of general compatibility.

UX and knowledge: registration_app.py, registration_workspaces.py, registration-ui/, persona-ui/, sitewide-ui/, knowledge_management.py and knowledge/. Analytics: platform_analytics.py, analytics_sources.py and Analytics-Operations.md. Source snapshot and frontend locks are also in ../github/nigeriag2p_withkms_Uxlevel/; reconcile differences with the running deployment before selecting a canonical repository. installed-versions.json records the original lab images; verify deployed versions independently.

## Required implementation and acceptance

1. Establish a reproducible, version-pinned deployment in OORU's environment. Capture custom patches, dependencies, schema migrations and configuration as version-controlled artifacts. Remove host-specific paths, demo accounts, shared credentials, mock identity and Example Bank from production. Configure secrets externally. Verify a clean installation and a full restore in an isolated environment.
2. Define authoritative ownership and contracts for household, beneficiary, application, programme and payment records. Replace or harden the custom synchronisation with durable, idempotent operations, conflict handling, observable retries and reconciliation. Test interrupted operations and duplicates across the portal, registry and PBMS. Support corrections after approval.
3. Integrate the National Social Register through an authorized NASSCO interface and NIN verification through an authorized NIMC interface. Obtain current access agreements, schemas, authentication, environments, rate limits, data-use restrictions and exception routes from their owners. Do not infer endpoints or assume direct database access. Keep registry membership, identity verification and programme eligibility separate; provide a human-reviewed route for missing or mismatched identity.
4. Implement versioned, access-controlled programme configuration for the confidential eligibility conditions, evidence, effective dates, benefit amounts and frequency. No decision or entitlement should run until the approved configuration is installed, independently checked and tested against agreed examples. Record the rule version and supporting evidence for each decision; implement correction and appeal procedures.
5. Integrate the nominated payment provider with separate preparation and authorization, idempotency, status inquiry, signed responses, settlement evidence and reconciliation. An unknown submission outcome must be resolved with the provider before any retry. Do not treat Bridge acceptance or a PBMS completed job as bank settlement. Test duplicate requests, timeouts, partial failures and reversals using the provider sandbox.
6. Replace sandbox access with production identity, least-privilege roles, programme and geographic scoping, separation of duties, audit trails, encrypted transport and storage, operational alerting, backup and disaster recovery. Assess privacy, retention, accessibility and security with the responsible owners. Analytics filters are currently not authorization boundaries; the existing backend aggregates have global scope.
7. Verify the end-to-end beneficiary and staff journeys using synthetic records and the actual deployment, including identity exceptions, eligibility, appeals, approval, provider reconciliation, accessibility, failure recovery and monitoring. Load-test expected peak volumes and complete independent security testing. Record evidence and named release decisions.

## Inputs required before production activation

- OORU's canonical repository, target hosting architecture, deployment access and accountable technical and programme owners.
- Authorized NSR/NIMC contracts and sandbox access, and the chosen payment provider's integration and settlement contracts.
- Approved confidential programme rules and test cases, role and geographic permission matrix, data retention and handling decisions, and operating procedures.
- Release evidence: migration and restore rehearsal, integrated acceptance and failure tests, security and accessibility assessment, operational readiness and formal programme/technical approval.

## Existing verification and limitations

The source documentation reports synthetic demo journeys and historical checks, not current production certification. The analytics dashboard reports operational and knowledge aggregates; it does not establish confirmed bank settlement. The intake and synchronization implementation is sandbox-specific, and a clean-machine restore has not been tested. See README.md, Registration-Integration-Operations.txt, Analytics-Operations.md and the test scripts for detailed scope. Re-run tests against the exact release candidate; do not represent historical demo results as production acceptance.
