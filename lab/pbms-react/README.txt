NSIPA PBMS current release — 16 November 2026

Read docs/current/INSTALLATION.md and docs/current/PBMS-PAYMENTS.md.
Programme setup -> enrolment -> disbursement -> Payment submits for approval ->
Finance -> Audit -> CEO -> Payment proceeds -> Bridge dispatch/reconciliation.
XLS export remains available. CEO approval alone does not send money.
The eleven red-marked sidebar entries are hidden; supporting routes/data remain.
Configure a sponsor bank route once per programme before payment submission.
The installed Bridge requires whole NGN entitlements; fractional values are rejected.
Existing account usernames/passwords are preserved. No passwords are published.
Build: npm ci; npm run build. Install the native addon, matching payment worker
extensions and session adapter in the sequence documented in INSTALLATION.md.
Tests create synthetic programmes and may send simulator payments. Run them only
in an isolated lab with verified local Example Bank connectors, never as installation.
Supply private approval credentials through PBMS_APPROVAL_ACCOUNTS_FILE.

Programme analytics: state/FCT map with programme/cycle filters and aggregate snapshot counts.
All five PBMS roles can view their assigned programmes. See docs/current/PROGRAMME-ANALYTICS.md.
