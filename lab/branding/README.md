# IQS Nigeria G2P branding

The IQS logo is the image supplied by the user on 13 October 2026. See [SOURCE.md](SOURCE.md).

## Running installation

The persistent Nginx gateway adds the local, same-origin CSS and JavaScript theme to HTML responses. It replaces visible OpenG2P text, titles, branding images and favicons, including newly rendered interface content. Odoo programme management, social registry and beneficiary programme administration also have the IQS company name and logo stored through their native company model. Staff, beneficiary and administration realms have IQS display names.

Programme-management and Keycloak login screens use a purple/white IQS layout with the original logo. Login forms, existing credentials, CSRF fields, OAuth routes, service hostnames and API payloads retain their functional identifiers. The source projects and license notices retain their upstream attribution. This is local presentation branding; it does not rename packages, rebuild every application image or convert the installed platform into an independently authored product.

Files are installed at `/opt/openg2p-lab/branding` and `/etc/nginx/snippets/iqs-brand.conf`. They survive service and WSL restarts. Reapply the gateway theme with `apply-iqs-branding.py` if gateway configuration is deliberately replaced; `brand-native-apps.py` applies native company/realm branding. The reapply script leaves original service URLs intact.

Original gateway configuration, launcher and company logos/names are saved privately at `/opt/openg2p-lab/branding-backup`. The existing pre-branding database backup is also retained. Updated backups now include the branding assets, launcher, baseline and Nginx configuration.

## Verification

Programme-management login succeeded after applying the theme. The authenticated registry dashboard retained 12 individuals, 6 households and the approved change request. The beneficiary portal retained the applied programme. Shared sign-in displays the IQS logo and login layout. All 68 workloads and 18 HTTPS entry points passed health checks. `verify-iqs-branding.py` checks injection in 12 interface responses and verifies all 3 served branding assets against the installed files without bypassing TLS validation.

Refresh existing browser tabs to load the new branding. URLs and usernames still contain `openg2p.localhost` because those are active integration identifiers. Do not globally replace those identifiers in source or configuration.
