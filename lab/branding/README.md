# NSIPA Nigeria G2P branding

The running application uses the SVG supplied by the user at `H:/Nigeria_Mosip/logo/NSIPA-Logo-Vector.svg`, adopted on 12 November 2026. The untouched source is retained as `nsipa-original-supplied.svg`; its checksum is in `replacement-logo-source.json`. All three SVG aliases (`nsipa-logo.svg`, `nsipa-wordmark.svg`, `nsipa-symbol.svg`) now use this complete outlined logo. Their viewports are fitted to the artwork without changing its paths or colors. PNG assets, including the legacy `iqs-logo.png`, are rendered from the same vector for compatibility.

The shared gateway theme covers visible brand text, logo images, embedded staff-service logos, titles, favicons, login/error/reset forms, and product attribution. Native company names/logos are updated in the three Odoo installations; staff, beneficiary and master realm display names are NSIPA. Login styling uses the green/gold palette. Staff catalogue icons and analytics branding are included. ODK vendor news and promotional feedback panels are hidden.

Authentication routes, database identifiers, record references, account names, API payloads and upstream source/license notices retain their existing technical values. Branding is a presentation customization. Do not globally rename service hostnames, cookies, package names or fixture IDs.

## Apply and verify

Build from `openg2p-lab/persona-ui` with `node build.cjs` after changing React source. Check `branding/iqs-brand.js` with `node --check` before deployment.

In Ubuntu-22.04 as root:

```
python3 /mnt/h/Nigeria_Mosip/codex/openg2p-lab/deploy_supplied_logo.py
```

Before deployment, build both `persona-ui` and `pbms-react` with `node build.cjs`. To adopt a new supplied SVG, run `node prepare-replacement-logo.cjs` in `pbms-react`, then `prepare_app_logo.py` in WSL. Deployment backs up changed files and the three native Odoo company logos under `/opt/openg2p-lab/logo-replacement-backups/`. It preserves current gateway/theme fixes and changes only logo assets, related sizing, explicit placeholder marks and company-logo fields. Verification covers 39 same-origin assets across 13 services and eight browser screens, including desktop/mobile MBR, staff sign-in, PBMS, the service hub, staff workspace, public atlas and Jos pilot. Results and screenshots are in `../../output/logo-replacement/`.

The old `apply-iqs-branding.py` and `brand-native-apps.py` entry points delegate to these installers. The deployed directory remains `/opt/openg2p-lab/branding` and the compatibility URL remains `/iqs-brand/`.

## Verification and recovery

135 checks across 15 public virtual hosts verify the five shared assets plus replacement Keycloak, OpenG2P, analytics and favicon URLs. All 70 workloads were ready after deployment. Browser checks covered public and authenticated pages; staff sign-in to field data succeeded. Evidence is in `../../outputs/nsipa-live-branding`.

Private rollback snapshot: `/opt/openg2p-lab/nsipa-branding-backups/20261103-024545` (assets, home pages, registration templates/static files and Nginx snippet). Native company/realm snapshots: `/opt/openg2p-lab/nsipa-native-backup`. Source snapshot: `../../outputs/nsipa-source-backup-20261103-024518`.

Refresh existing browser tabs to load the new versioned theme.
