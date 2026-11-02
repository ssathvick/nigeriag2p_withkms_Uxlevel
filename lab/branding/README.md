# NSIPA branding

The Nigeria G2P lab uses the original NSIPA Shared Progress identity. Editable Illustrator, SVG and Photoshop masters are in [source](source/READ-ME.txt). This is a demonstration identity proposal, not an adopted official government mark. The outlined web assets work without installed fonts. `nsipa-wordmark.svg` is the compact navigation logo; `nsipa-symbol.svg` is the favicon; `nsipa-logo.svg` is the full signature.

The shared theme replaces visible IQS, OpenG2P, Keycloak, ODK and analytics branding, including staff-service logos, login pages, titles, favicons and product attribution. Native Odoo company logos and Keycloak realm display names are set by the native installer. Existing `/iqs-brand/` URLs are retained for compatibility. Authentication routes, API identifiers, record references and upstream license/source notices retain their technical values.

## Install on an existing lab

Prerequisites: the existing Nigeria lab deployed under `/opt/openg2p-lab`, its gateway Nginx snippet, registration service, Kubernetes namespace and locally provisioned credentials. These scripts customize that installation; they are not a fresh platform installer. Build with Node.js/npm, then run the Python scripts as root in the lab's Ubuntu environment (Python requests and PyYAML required).

From this repository's `lab` directory (inside `latest-source` in the recovery repository):

```sh
cd persona-ui
npm ci
npm run build
cd ..
node --check branding/iqs-brand.js
python3 apply-nsipa-branding.py
python3 brand-native-nsipa.py
python3 verify-nsipa-branding.py
```

Run scripts from the checkout or a staged copy that contains the built `persona-ui/dist` files. The old `apply-iqs-branding.py` and `brand-native-apps.py` entry points delegate to the NSIPA installers. After restoring a historical recovery archive, apply these current sources to obtain NSIPA branding.

## Verification and rollback

`nsipa-verification.json` records the 3 November 2026 live deployment: 135 asset checks across 15 virtual hosts and 70 ready workloads. Rerun the verifier for the current installation. Browser checks also covered public and authenticated pages, including staff sign-in, field data and analytics.

The shared installer creates private timestamped snapshots under `/opt/openg2p-lab/nsipa-branding-backups` and restores the snapshot automatically if installation fails. Native pre-change company and realm data are saved under `/opt/openg2p-lab/nsipa-native-backup` for manual recovery. Keep these runtime backups and credentials outside Git. Refresh browser tabs after applying the versioned theme.
