# NSIPA beneficiary screens

Enabled on 10 November 2026:

- `https://beneficiary.nigeriag2p.com/selfservice/en/accounts`
- `https://g2p-beneficiary.wverve.in/selfservice/en/accounts`

Replace `accounts` with `complaints`, `notifications`, `news` or `registries` for the other screens. All five are linked from existing beneficiary pages and share the existing backend data across both domain families.

## Behaviour

- Accounts resolve, link, update and unlink the signed beneficiary household mapping through the installed mapper/keymanager. Only approved, fully synchronised households can change mappings. The installed bank connector is `EXAMPLE_BANK`; this sandbox accepts fictional `LAB-` accounts. Saving a mapping does not verify bank ownership, create a bank account or initiate payment.
- Complaints use the existing grievance endpoint, including its identity checks, submission idempotency, deadlines, staff lifecycle and audit records. The installed workflow records structured reasons; free-text descriptions and attachments are not supported by that backend.
- Notifications derive from the signed-in beneficiary's existing registration/account audit, application records and complaint events. Read receipts are stored in an additive `beneficiary_notification_reads` table in the existing intake database. No external notification provider or outgoing messages were introduced.
- News reads only existing published, non-archived news content. Search, full article expansion and published English/Hausa/Yoruba/Igbo variants are available. Existing staff publishing controls remain authoritative.
- Registries displays the beneficiary's installed household register and links to the existing registration form. A narrowly scoped login intent preserves the profile destination; the form links back to the matching beneficiary domain. Existing review, correction, synchronisation and approved-record locking remain in place.

## Runtime and source

React sources: this directory; build with `node openg2p-lab/beneficiary-extra/build.cjs` from the workspace root. It reuses the installed React/esbuild dependencies in `pbms-react/node_modules`.

Runtime: `/opt/openg2p-lab/beneficiary-extra`; systemd service `iqs-beneficiary-extra`, loopback port 18115. Nginx configuration: `/etc/nginx/conf.d/beneficiary-extra.conf`. Existing native beneficiary routes and backend services continue unchanged. `server.py` verifies native Keycloak JWT signatures, issuer, audience, authorised client and expiry, then derives ownership exclusively from the signed subject. Mutations require origin checks and a token-bound CSRF value. Secrets remain in the protected runtime config, outside static assets.

Deployment scripts: `deploy.py`, `fix-handoff.py`, `publish-help.py`. These are deployment/maintenance tools, not scripts to run on every request. The help publication preserves version history and updates six published records, including the citizen household guide. Existing unrelated drafts must be reconciled before a maintenance publication.

Original Nginx/service/config/database backups are under `/opt/openg2p-lab/beneficiary-extra/backups/20261110-144021`; the registration callback backup is under `backups/handoff-20261110-144441`. For rollback, restore the relevant configuration/code and reload the affected service. Do not restore whole databases over subsequent user activity simply to remove the frontend; the additive read-receipt table can remain.

## Verification evidence

- `smoke-results.json`: authenticated API reads for all five screens on both domains.
- `workflow-results.json`: signed mapper link/update/unlink, stale-write rejection, original fictional account restoration, cross-domain complaint retry, notifications, published news/search/languages, CSRF/origin checks and anonymous rejection.
- `final-results.json`: final registration round-trip and native profile navigation on both domains, correct existing simulator bank routing, staff acknowledgement/escalation/resolution, beneficiary visibility on both domains and a second beneficiary's isolation.
- `release-audit.json`: final ten screen checks with complete contextual help, NSIPA naming, mobile overflow checks, account removal cancellation/invalid input validation, notification read persistence and no JavaScript page errors.
- `help-*.png`: mobile contextual-help captures. Guidance is scrollable; text is retained in full rather than line-clamped.

The synthetic verification complaint is resolved and retained in the existing audit trail. The original fictional account is restored to `LAB-HH-000001` with the configured `EXAMPLE_BANK` route. No real payment was initiated. Registry registration writes continue through the existing form; this release verified the authenticated handoff and approved-record protection rather than creating another household.
