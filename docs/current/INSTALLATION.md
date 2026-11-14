# Install the current NSIPA application on another machine

Release: **14 November 2026**. Read the repository README first. Commands below run in Ubuntu 22.04, including Ubuntu under WSL2. They assume the current source has been staged as `/opt/nsipa-current/lab`. Each stage has its own checkpoint; this is a guided installation of the actual applications, not an unattended installer.

## 1. Choose installation or state migration

A fresh installation creates new identities, empty operational databases and new programme IDs. Git contains application source and configuration examples. The existing site's accounts, household records, approved lists and credentials are not recreated by cloning.

For an exact operational migration, separately transfer encrypted PostgreSQL dumps, Odoo filestore, registration/ODK synchronization state, application secrets and the matching volume backups. Restore to an isolated destination and reconcile them before allowing writes. Do not transfer the original public tunnel identity or attach another machine to its public DNS. Recorded videos, voice samples, Camtasia projects and XLS exports are deliberately outside this source release.

## 2. Prepare the host

Planning baseline from the full-lab guide: Windows 11 x64 with virtualization, WSL2 Ubuntu 22.04 with systemd, 12–16 logical processors, 64 GB host RAM as a practical starting point, and at least 150 GB free SSD space. The original lab allocated 48–64 GB to WSL and 16 GB swap. These are planning figures, not proof that a smaller machine can run the full cluster. A native Linux adaptation requires its own acceptance run.

Install Git, Python 3 with venv, unzip, Node.js 22/npm, Docker, kubectl and Helm. The full-lab guide establishes K3s, Istio ingress, local TLS and the upstream applications; follow its pinned installation stages rather than installing arbitrary latest charts. Only Node/Python are needed for building individual frontend packages, but a working backend and identity service are required to use them.

From Windows, check `wsl --list --verbose`; Ubuntu must use version 2. Enable systemd and set resource limits as described in the installation guide. Preserve other WSL distributions and existing `.wslconfig` settings.

## 3. Install the base services

The public [iqs-nigeria-g2p repository](https://github.com/ssathvick/iqs-nigeria-g2p) carries `IQS-Nigeria-G2P-Recovery-Bundle.zip`, `BUNDLE.sha256`, the root installation Word guide, and the Windows preparation launchers. The UX repository uses that same installation baseline.

Windows: run `Prepare-Full-Lab.bat` from the IQS checkout. It verifies and extracts into a new staging directory; it does not install the cluster. Alternatively, inside the IQS checkout in Ubuntu:

```bash
sha256sum IQS-Nigeria-G2P-Recovery-Bundle.zip
cat BUNDLE.sha256
mkdir recovery
unzip -n IQS-Nigeria-G2P-Recovery-Bundle.zip -d recovery
mkdir base-kit
unzip -n recovery/iqs-nigeria-g2p/installation/IQS-Nigeria-Installation-Kit.zip -d base-kit
```

Compare the printed hash before extracting. Use unused directories. Follow `IQS-Nigeria-OpenG2P-Installation-Guide.docx` for copying `base-kit/IQS-Installation-Kit` to `/opt/openg2p-install`, installing tools and shared services, Registry, IAM, AWE, PBMS, Bridge, portal, Nginx and local CA, in that order. Follow the guide's commands and readiness gates, not alphabetical execution of `lab/*.py`.

The bundle is historical. Before applying the current overlay, reconcile its charts and services with `source-snapshots/2026-11-14-nsipa/runtime-images.json`. Particularly important current runtime versions are:

| Service | Version used for the source patches |
| --- | --- |
| Native Registry staff API | `openg2p/openg2p-registry-staff-api:1.2.1`, Python 3.12 module paths |
| AWE | `openg2p/openg2p-awe:1.2.2`, Python 3.13 module paths |
| PBMS | `openg2p/openg2p-pbms-core:3.0.0`, Odoo 17 |
| Master Registry frontend | Build `registry-ui-source/Dockerfile.native` here; `nsipa/*` tags are local build outputs, not guaranteed public images |

The image inventory records observed tags, not a standalone Helm release or immutable digest lock for every image. Do not simply replace image tags against an incompatible database schema. Upgrade upstream charts/schema to the matching versions using their migration sequence first. The module mount paths in `meeting-native/changes.json` must exist in the destination images. The older kit alone is insufficient evidence that these new native prerequisites are ready.

Checkpoint:

```bash
kubectl -n nigeria get pods
kubectl -n nigeria get deployments
kubectl -n nigeria get services
kubectl -n nigeria rollout status deployment/register-staff-portal-api --timeout=240s
kubectl -n nigeria rollout status deployment/commons-services-awe --timeout=240s
kubectl -n nigeria rollout status deployment/pbms-odoo --timeout=240s
```

Also check persistent volumes, database connectivity, staff Keycloak realm, IAM permissions, AWE Registry policies, TLS trust and native sign-in. Create and test the base household/individual definitions before applying the survey overlay. Expected services include `commons-postgresql`, `commons-keycloak`, `commons-services-iam-staff-portal-api`, `pbms-odoo`, and `bridge-api`. The source expects the `register`, `awe`, `iam` and `pbmsdb` databases. A different namespace/service/schema layout requires adaptation before executing the installers.

## 4. Stage current source and destination domains

Set `LAB_SOURCE` to `lab` in the UX checkout or `latest-source/lab` in the IQS checkout. Use an absolute path:

```bash
LAB_SOURCE="$PWD/lab" # UX repository; for IQS use "$PWD/latest-source/lab"
cp "$LAB_SOURCE/release/deployment.example.json" /tmp/nsipa-deployment.local.json
```

Edit all hostname mappings in that local file for a domain you control. Add mappings for other configured service hostnames when required. For a local-only installation, choose the established local hostnames and matching certificates from the base guide. These files contain no passwords.

```bash
sudo python3 "$LAB_SOURCE/release/prepare_source.py" \
  --source "$LAB_SOURCE" --destination /opt/nsipa-current/lab \
  --config /tmp/nsipa-deployment.local.json
SOURCE=/opt/nsipa-current/lab
```

This creates a new tree, adapts original `/mnt/h/...` source references and configured hostnames, and leaves both the checkout and running services untouched. It refuses a nonempty destination. The runtime path remains `/opt/openg2p-lab`; this is deliberate compatibility with the staged base platform. Review remaining original-machine references before use:

```bash
rg 'wverve\.in|nigeriag2p\.com|/mnt/h/|H:\\' "$SOURCE" \
  -g '*.py' -g '*.ts' -g '*.tsx' -g '*.js' -g '*.conf'
```

Some historical diagnostics retain fixture IDs, private credential paths and old hostnames. They are not installer stages. Replace service hosts in Nginx/Istio, DNS, OIDC redirect and logout allowlists, cookie domains, application URL settings, CORS/Origin allowlists, ODK configuration and optional analytics connectors together. Changing only a React URL is insufficient.

Create destination secrets outside Git, including `/opt/openg2p-lab/credentials.yaml` generated by the base setup. Set private files to mode 0600 and their parent directories to 0700. Do not use passwords from examples or restore the original Cloudflare tunnel.

## 5. Install the Python runtime and registration utilities

The base registration integration must already have created its configuration, templates, service unit and data directory. If it is absent, complete the base registration stage from `docs/REINSTALL.md` in the extracted recovery tree, then review the current source installer `install-registration-integration.py`. Do not replace live private configuration with a source example.

```bash
sudo python3 -m venv /opt/openg2p-lab/registration-venv
sudo /opt/openg2p-lab/registration-venv/bin/pip install -r "$SOURCE/registration-requirements.txt"
sudo /opt/openg2p-lab/registration-venv/bin/pip install qrcode
sudo systemctl status iqs-registration --no-pager
```

Pin the resolved `qrcode` version in your destination deployment record. The registration runtime supplies the service gateway, knowledge tools, native Registry staff directory and Collect setup utility. Native Registry/AWE remain the approval authority.

Build the shared persona/navigation assets using the lockfile:

```bash
cd "$SOURCE/persona-ui"
npm ci
npm run build
```

Review `install-persona-workspaces.py` before using it on a new base; it expects the initialized registration service, templates and intake database. It takes a private backup and deploys the workspace assets. Its historical browser walkthrough is distinct from native Registry operations. Deploy the current registration modules/templates required by the modules enabled in `registration_app.py`, retaining destination configuration, service account access and knowledge data. `install-persona-workspaces.py` is not a full replacement for the staged registration installation.

## 6. Native Registry backend, roles and UI

Do not run `deploy-mbr-workflow.py`, `deploy-mbr-integration.py`, `mbr_native_migration.py`, or enable `iqs-mbr-native-import.timer` as a fresh-install recipe. Those are historical supplemental-owner migration tools. Do not run `restore_native_registry_authority.py` on an empty new database; it is a migration/recovery tool for the original cutover.

The release contains the already-reviewed native patches in `meeting-native/patched/`, their original module references in `meeting-native/original/`, and the deployment map in `meeting-native/changes.json`. Do not regenerate these with capture/prepare scripts against a different upstream version and assume equivalent results.

```bash
cd "$SOURCE"
sudo /opt/openg2p-lab/registration-venv/bin/python deploy_meeting_native_backend.py
sudo /opt/openg2p-lab/registration-venv/bin/python configure_native_enumerator_choices.py
sudo /opt/openg2p-lab/registration-venv/bin/python remove_enumerator_selector.py
```

The backend stage backs up Registry/AWE, adds survey/history columns and mounts version-scoped modules into the staff API, AWE and relevant workers. The date/name of the scripts is historical; the committed patched files are the final release. The final two stages set the reviewed consent/sponsor metadata and ensure the enumerator selector is absent without deleting stored values. Do not use sample names as evidence of real staff identities. Inspect rollouts for every deployment listed in the map and the related worker deployments.

Create five distinct destination identities in the staff Keycloak realm first, using the destination IAM administration tools. Use your own logins and temporary passwords. Copy `release/registry-accounts.example.json` outside Git and enter those existing usernames. Then inspect the role plan and apply:

```bash
sudo /opt/openg2p-lab/registration-venv/bin/python integrate_native_registry_accounts.py \
  --accounts /secure/registry-accounts.local.json
sudo /opt/openg2p-lab/registration-venv/bin/python integrate_native_registry_accounts.py \
  --accounts /secure/registry-accounts.local.json --apply
```

This configures the native Keycloak client roles, IAM permission mappings and new versioned Registry AWE policies. The designated first/second reviewer usernames determine the two stage assignments. Existing identity passwords, required actions and historical decisions are preserved. Review the plan and account file before applying it to existing identities; native client role grants are reconciled for those identities. The Registry Administrator receives the IAM administration role needed by staff provisioning. Bootstrap administration is a separate duty from approving records.

Install the authenticated utilities only after their runtime dependencies exist. `deploy_native_offline_setup.py` also expects an initialized private ODK synchronization directory/configuration:

```bash
sudo /opt/openg2p-lab/registration-venv/bin/python deploy_native_offline_setup.py
sudo /opt/openg2p-lab/registration-venv/bin/python deploy_native_registry_users.py
```

For ODK capture, establish the destination ODK project, OIDC connection and private synchronization configuration first; then review/run `publish_native_collect_form.py`. It publishes `meeting-native/nsipa_registry_household.xml` and installs the native section mappings. The field agent obtains their own private Collect QR from **Offline field capture**; never commit that QR or its App User URL. Offline physical-device/reconnect acceptance must be repeated on the destination.

Configure `registry-ui-source/.env.local` from `.env.example` with destination backend, master-data, IAM, Keycloak logout, cookie-domain and redirect values. Set server-side `NSIPA_REGISTRATION_URL` to the destination registration base, including `/registration`. All token-bearing utility requests must stay on destination-owned services. Ensure the container also receives the relevant runtime variables through its deployment configuration.

```bash
cd "$SOURCE/registry-ui-source"
docker build -f Dockerfile.native -t nsipa/master-registry:release-20261114 .
cd "$SOURCE"
sudo /opt/openg2p-lab/registration-venv/bin/python deploy_meeting_native_ui.py \
  nsipa/master-registry:release-20261114
kubectl -n nigeria rollout status deployment/register-staff-portal-ui --timeout=240s
```

`deploy_meeting_native_ui.py` imports the locally built image into K3s. It assumes a single local Docker/K3s node. For a multi-node cluster, push the image to your registry and configure pull access on every node instead. The container listens on port 3000 and must be served behind the destination gateway. Verify staff sign-in, permission loading, configuration metadata and the API proxies before a workflow test.

## 7. Install the PBMS approval backend

Install against the initialized PBMS 3 database, not the separate legacy beneficiary-portal programme model. The image must have `xlwt` for native BIFF XLS output. The installer checks it before changing the deployment; if missing, add it to a reproducible PBMS image build, deploy that image, and retry. Do not rely on a temporary pip install inside a running pod.

```bash
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/install_pbms.py"
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/install_pbms.py" --apply
```

The first command prints the plan. The second authenticates using the destination private credentials, backs up PBMS PostgreSQL and the deployment, applies `nsipa-approval-addon`, mounts it persistently, waits for rollout, and installs/upgrades `nsipa_approval`. It supports `--namespace`, `--deployment`, `--database`, `--postgres-pod`, `--admin-login` and `--backup-root`; inspect `--help`. `PBMS_CREDENTIALS_FILE` can point to another private YAML file. It never creates programme fixtures or dispatches bank payments.

## 8. Deploy PBMS React and its authenticated adapter

```bash
cd "$SOURCE/pbms-react"
npm ci
npm run build
sudo mkdir -p /opt/openg2p-lab/pbms-react/backups
sudo /opt/openg2p-lab/registration-venv/bin/python install-adapter.py
sudo systemctl status pbms-react-api --no-pager
```

The adapter discovers destination Kubernetes service addresses and binds to loopback port 18112. For an Origin other than those prepared into the source, add `PBMS_ALLOWED_ORIGINS=https://your-pbms-host` to its private `adapter/service.env`, then restart `pbms-react-api`. Keep the Odoo session cookie, exact Origin and the authenticated user's permissions; no admin key belongs in this service or in React.

Install the `dist/` build in a timestamped release under `/opt/openg2p-lab/pbms-react/releases/`, with `current` as a symlink to it. Retain the previous symlink target for rollback. Copy the reviewed branding assets to `/opt/openg2p-lab/branding/`, preserving `nsipa-logo.svg` with its words. The historical `deploy-pbms-react.py` automates this only for the original Nginx site layout; a different destination should use the prepared `release/pbms.nginx.example.conf` instead of running that script blindly.

Review that Nginx example, its TLS certificate/key paths and ingress upstream, then enable it as a dedicated PBMS site. Remove conflicting PBMS host declarations from older sites while preserving unrelated hosts. Istio/upstream routing must recognize the destination PBMS Host header. Preserve `/web/session/*`, `/web/dataset/*`, document routes and other backend routes through the same origin. Serve `/pbms-ui/` from `current`, `/pbms-ui-api/` from loopback 18112, `/iqs-brand/` from the branding directory, and keep `/web?native=1` for recovery administration.

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://YOUR-PBMS-HOST/pbms-ui/
```

Only reload after a successful config check. Do not disable TLS verification to bypass trust problems. Configure the service portal's PBMS block to point to this destination PBMS entry.

## 9. PBMS accounts and programme membership

Copy `release/pbms-accounts.example.json` to a private destination file and replace its five logins. The following utility is for the five PBMS internal accounts, which are distinct from Registry's Keycloak accounts:

```bash
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/provision_pbms.py" \
  --accounts /secure/pbms-accounts.local.json --output /secure/pbms-created.local.json
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/provision_pbms.py" \
  --accounts /secure/pbms-accounts.local.json --output /secure/pbms-created.local.json --apply
```

The first command is a plan and does not create the output. Apply creates missing users with generated passwords, saves those only to a mode-0600 private file, and preserves existing passwords. After Programme Admin creates a programme, a **staff access administrator** must grant the five roles access to that programme through its **Staff access** tab. Alternatively rerun the utility with `--programme-id NEW_ID` and a new private output filename. Do not hardcode programme 48/53, list 38, or old account IDs on a new database. A Programme Admin does not automatically receive general staff-access administration.

Use the walkthrough in [USAGE.md](USAGE.md). Keep role duties separate and test permission denials as well as the successful path.

## 10. Destination acceptance, operations and rollback

Before treating the new machine as ready:

- Verify five native Registry accounts and five PBMS accounts separately, including unauthorized actions, sign-out/session expiry and correct return destinations.
- Capture a fictional household and individual, save drafts, submit, review at both stages, return/correct/resubmit, reject, and verify final native master/history records. A creator or first reviewer must not approve the second stage.
- Check search/filter/pagination, readable labels, member age/date-of-birth handling, consent, duplicate review and mobile layout. Verify the final survey has no enumerator selector.
- If ODK is enabled, test the full form in airplane mode, reconnect, confirm one native intake and retained device copy, then perform both native reviews. Repeating synchronization must not create duplicates.
- Run a new PBMS programme through configuration, closed registration dates, scheduled list processing, Payment submission, Finance/Audit/CEO review and native XLS export. Verify actual exported amounts and status after restarting services.
- Reject at each PBMS approval level, make a reasoned correction as Programme Admin, resubmit as Payment, and verify all three approvals restart for the new revision. Test direct export and approval access from the wrong account and before readiness.
- Verify knowledge publication and contextual help, optional analytics source freshness and the service portal links that you configured. Optional Ollama/analytics/field previews are separate components, not prerequisites for native PBMS approval.
- Record the destination's charts/images, installed addon, mounts, cron activity, URLs, tests, backup hashes and restore result. Historical test results do not certify this new machine.

Useful diagnostics:

```bash
kubectl -n nigeria get pods,pvc
kubectl -n nigeria logs deployment/register-staff-portal-api --tail=100
kubectl -n nigeria logs deployment/commons-services-awe --tail=100
kubectl -n nigeria logs deployment/pbms-odoo --tail=100
sudo journalctl -u iqs-registration -u pbms-react-api --since '15 minutes ago'
sudo nginx -t
```

Do not post raw logs or database dumps publicly; they may contain personal data or tokens. Source checks, frontend builds and helper plan modes can be run locally without touching operational data. Most retained `test-*`, `prepare-*`, `cleanup-*`, `verify-*` and `finalize-*` scripts are original-environment diagnostics/fixtures; review their service names and private inputs before use. Never execute the whole directory as a test suite against a real deployment.

PBMS lists move from Pending to Complete through the scheduled Odoo worker, normally once a minute. If stuck, inspect the scheduled action and list error, fix its cause, then retry/refresh; do not manually force a status to Approved. A 403 usually means an Origin, native role or programme-membership mismatch. Utility failures often mean a wrong `NSIPA_REGISTRATION_URL`, missing Keycloak client-role/IAM mapping, missing CA trust, or an uninitialized ODK project. Missing backend RPC methods indicate the addon was not installed/upgraded.

For a frontend-only rollback, repoint `current` to its prior release, validate Nginx, and reload. For Registry/AWE module rollback, use the matching backed-up deployment/ConfigMap and schema recovery point. For PBMS backend rollback, use the saved deployment and matching database/filestore recovery point with writes stopped and post-backup activity reconciled. Rolling back source alone does not undo schema changes, role grants, approvals or history. Do not delete audit records or replay payment actions as a recovery shortcut.

Both repositories remain public. Fresh-machine replay of this release has not been performed; the release provides current source, tested local builds and a staged installation procedure, not a claim of unattended installation or production acceptance.
