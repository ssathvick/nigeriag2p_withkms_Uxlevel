# NSIPA Nigeria G2P branding

The running site uses the original NSIPA Shared Progress identity created on 3 November 2026. Vector masters are in `../../NSIPA-Identity`. `nsipa-logo.svg` is the full signature, `nsipa-wordmark.svg` is the compact emblem/acronym lockup, and `nsipa-symbol.svg` is the standalone emblem. SVG type is outlined. The legacy `iqs-logo.png` URL now serves NSIPA for backward compatibility.

The shared gateway theme covers visible brand text, logo images, embedded staff-service logos, titles, favicons, login/error/reset forms, and product attribution. Native company names/logos are updated in the three Odoo installations; staff, beneficiary and master realm display names are NSIPA. Login styling uses the green/gold palette. Staff catalogue icons and analytics branding are included. ODK vendor news and promotional feedback panels are hidden.

Authentication routes, database identifiers, record references, account names, API payloads and upstream source/license notices retain their existing technical values. Branding is a presentation customization. Do not globally rename service hostnames, cookies, package names or fixture IDs.

## Apply and verify

Build from `openg2p-lab/persona-ui` with `node build.cjs` after changing React source. Check `branding/iqs-brand.js` with `node --check` before deployment.

In Ubuntu-22.04 as root:

```
python3 /mnt/h/Nigeria_Mosip/codex/openg2p-lab/apply-nsipa-branding.py
python3 /mnt/h/Nigeria_Mosip/codex/openg2p-lab/brand-native-nsipa.py
python3 /mnt/h/Nigeria_Mosip/codex/openg2p-lab/verify-nsipa-branding.py
```

The old `apply-iqs-branding.py` and `brand-native-apps.py` entry points delegate to these installers. The deployed directory remains `/opt/openg2p-lab/branding` and the compatibility URL remains `/iqs-brand/`.

## Verification and recovery

135 checks across 15 public virtual hosts verify the five shared assets plus replacement Keycloak, OpenG2P, analytics and favicon URLs. All 70 workloads were ready after deployment. Browser checks covered public and authenticated pages; staff sign-in to field data succeeded. Evidence is in `../../outputs/nsipa-live-branding`.

Private rollback snapshot: `/opt/openg2p-lab/nsipa-branding-backups/20261103-024545` (assets, home pages, registration templates/static files and Nginx snippet). Native company/realm snapshots: `/opt/openg2p-lab/nsipa-native-backup`. Source snapshot: `../../outputs/nsipa-source-backup-20261103-024518`.

Refresh existing browser tabs to load the new versioned theme.
