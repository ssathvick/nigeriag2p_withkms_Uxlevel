# Nigeria G2P â€” Master Registry, personas, PBMS and KMS

**Current application source: 14 November 2026. This repository is public.**

This release contains the updated Master Beneficiary Registry UI, native Registry/AWE review workflow, staff personas and roles, shared knowledge/navigation, and the native PBMS programme-to-disbursement approval flow. These are changes to the actual applications. A separate standalone Experience Kit remains available for previewing the reusable UX/KMS template.

The source can be cloned without a GitHub access grant. Signing into the deployed applications still requires destination-specific accounts and permissions. No running database, original account passwords, private keys, tunnel credentials, Camtasia recording or voice sample is included.

## Start here

1. Read the installation path below and the detailed [current installation guide](docs/current/INSTALLATION.md).
2. Use the [step-by-step application walkthrough](docs/current/USAGE.md) for the five Registry roles and the five PBMS accounts.
3. Inspect the [release inventory](source-snapshots/2026-11-14-nsipa/README.md), [source hashes](source-snapshots/2026-11-14-nsipa/source-manifest.json) and [observed runtime images](source-snapshots/2026-11-14-nsipa/runtime-images.json).

## What changed

| Area | Current implementation |
| --- | --- |
| Master Registry UI | Role-aware overview, household and individual capture/details, readable labels, review/history, search/filter/pagination, configuration tools and responsive layouts |
| Native reviews | Registry/AWE backend patches for independent two-stage review, return for correction, rejection, resubmission and retained history; native services remain the workflow owner |
| Registry staff | Registration Officer, Field Agent, Approver 1, Approver 2 and Registry Admin, with native Keycloak/IAM permission mappings |
| Survey and offline | Consent/sponsor/respondent/community and household/member fields; final survey without enumerator selector; authenticated staff and Collect setup utilities |
| PBMS setup | Cash Benefit Code in NGN, programme mapping, eligibility/entitlement rules, NGN 25,000 maximum, monthly enrolment/disbursement cycles and scheduled list calculation |
| PBMS approvals | Separate Programme Admin, Payment, Finance, Audit and CEO accounts; programme-scoped access, comments/evidence, sequential decisions, rejection/correction and revision history |
| Final output | Programme Admin downloads a native `.xls` after all three approvals; export checks the current list content and records its history |
| Branding | Existing NSIPA logo with words retained; sections designated for later removal remain available |

The final PBMS approval/export policy does not send payments. Legacy payment programmes remain separate. Master Registry and PBMS have distinct native models; their synchronization adapter must be configured and verified on the new machine.

## Repository layout

| Path | Purpose |
| --- | --- |
| `lab/registry-ui-source/` | Current Next.js/React native Master Registry frontend and Docker build |
| `lab/meeting-native/` | Reviewed Registry/AWE module patches, originals and deployment map |
| `lab/pbms-react/src/` | Actual PBMS React screens and approval flow |
| `lab/pbms-react/nsipa_approval/` | Native Odoo 17 addon: persisted rules, cycles/lists, roles, approvals, corrections, history, cron and XLS |
| `lab/pbms-react/workflow_api.py` | Session-bound adapter for the connected frontend; no browser admin key |
| `lab/persona-ui/`, `registration-ui/`, `knowledge/`, `branding/` | Shared personas/navigation, gateway, guidance and established NSIPA identity |
| `lab/release/` | Destination-source preparation, PBMS install plan/apply, account provisioning and configuration examples |
| `docs/current/` | Current installation, use, validation, troubleshooting and rollback instructions |
| `source-snapshots/` | Dated release manifests; earlier snapshots/packages remain historical |

The base recovery kit and installation/operations guides are in the public [iqs-nigeria-g2p repository](https://github.com/ssathvick/iqs-nigeria-g2p). The current application source in this repository is `lab/`.

## Clone and prepare

```bash
git clone https://github.com/ssathvick/nigeriag2p_withkms_Uxlevel.git
cd nigeriag2p_withkms_Uxlevel
LAB_SOURCE="$PWD/lab"
```

For the complete platform, use Ubuntu 22.04 with systemd, K3s/Kubernetes, Helm, ingress/TLS, Docker, Python/venv and Node.js 22. On Windows use WSL2. The full-lab planning baseline is 12Ã¢â‚¬â€œ16 logical processors, 64 GB host RAM and 150 GB free SSD; see the detailed guide for qualifications and WSL settings. A standalone frontend build needs fewer resources but does not replace its backend.

The [IQS installation repository](https://github.com/ssathvick/iqs-nigeria-g2p) includes the historical pinned base kit, Windows preparation launchers and installation/operations Word guides. Install the base in its documented stages first, then reconcile Registry staff API 1.2.1, AWE 1.2.2 and PBMS 3/Odoo 17 with the current release inventory. The older kit alone does not automatically install this new overlay.

Prepare destination paths and hosts without modifying the live system:

```bash
cp "$LAB_SOURCE/release/deployment.example.json" /tmp/nsipa-deployment.local.json
# Edit the local file with your own service hostnames first.
sudo python3 "$LAB_SOURCE/release/prepare_source.py" \
  --source "$LAB_SOURCE" --destination /opt/nsipa-current/lab \
  --config /tmp/nsipa-deployment.local.json
SOURCE=/opt/nsipa-current/lab
```

The helper requires a new empty destination. It adapts original source paths/hosts, omits local dependencies and private/runtime artifacts, and does not deploy services. Set new DNS, TLS, OIDC callbacks, cookie domains, ingress routes and allowed origins consistently. Generate destination secrets privately; never reuse this installation's tunnel identity.

## Install the current overlay

The [detailed installation guide](docs/current/INSTALLATION.md) gives prerequisites, exact sequencing and checkpoints for every step below. Complete the base platform and registration integration before these stages.

1. Install the registration Python dependencies and `qrcode` in the destination venv. Build `persona-ui` with `npm ci` and `npm run build`, and deploy its reviewed modules/assets into the initialized registration service.
2. Apply `deploy_meeting_native_backend.py` to the matching Registry/AWE versions. Apply the final survey metadata stages documented in the guide. These take private backups and mount the reviewed native patches persistently.
3. Create five distinct Registry staff identities in the destination staff realm. Populate a private copy of `release/registry-accounts.example.json`. Inspect, then apply `integrate_native_registry_accounts.py --accounts /secure/registry-accounts.local.json --apply`. Passwords and historical decisions are preserved; the supplied first/second reviewer identities determine the versioned AWE policies.
4. Install the authenticated staff/field utilities after their dependencies exist. Configure `registry-ui-source/.env.local` and runtime variables, including `NSIPA_REGISTRATION_URL`. Build `Dockerfile.native`, import/deploy it with `deploy_meeting_native_ui.py`, and verify native sign-in and both review stages.
5. Install the PBMS native addon using the new portable helper:

```bash
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/install_pbms.py"
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/install_pbms.py" --apply
cd "$SOURCE/pbms-react"
npm ci
npm run build
sudo /opt/openg2p-lab/registration-venv/bin/python install-adapter.py
```

The first addon command only prints a plan. Apply verifies the `xlwt` XLS dependency and administrator access, backs up PBMS and the deployment, installs the persistent ConfigMap mount and installs/upgrades `nsipa_approval`. It does not seed programmes or invoke bank payments. The frontend build and adapter require the native addon; static assets alone cannot implement this flow.

6. Publish `pbms-react/dist/` as a versioned static release with a `current` symlink. Configure Nginx with the prepared `release/pbms.nginx.example.conf`, proper destination TLS/ingress and `/pbms-ui-api/` loopback routing. Validate `nginx -t` before reload. Configure `PBMS_ALLOWED_ORIGINS` when required.
7. Use a private copy of `release/pbms-accounts.example.json` and `release/provision_pbms.py` to create the five PBMS accounts. Newly generated passwords are written only to a private mode-0600 file; existing passwords are preserved. A separate staff access administrator grants each account access to each new programme. Do not reuse original record IDs or expect the source clone to contain the recorded demo's data.
8. Run the destination acceptance checklist in the installation guide, including both successful and denied actions, rejection/resubmission, restart persistence and XLS contents.

Do not execute all retained scripts as an installer. In particular, the older supplemental `deploy-mbr-workflow.py`, `deploy-mbr-integration.py` and `iqs-mbr-native-import.timer` are retired for current Registry ownership. Earlier private backup/cutover scripts are historical recovery tools, not fresh-database setup stages.

## Use the new workflows

Registry: sign in as Registration Officer/Field Agent, capture a draft and submit; Approver 1 then Approver 2 review independently; inspect the resulting native master/history. Returned records follow correction/resubmission; permanent rejections remain locked. Registry Admin manages staff/configuration and does not perform approval duties. See [Registry use and field setup](docs/current/USAGE.md).

PBMS:

1. From the service portal, open the PBMS block and sign in as **Programme Admin**.
2. Open **Programme approval flow**, create an active programme, select the base registry, create/map an NGN cash Benefit Code, set the entitlement and eligibility criteria, and select Finance/Audit/CEO groups. Save configuration.
3. Create the monthly enrolment cycle. After registration closes, create its list and wait for scheduled processing/auto-approved enrolment.
4. Create the linked disbursement cycle and list; review the beneficiary count, individual amounts and total.
5. **Payment** submits the list for approval with a comment.
6. **Finance**, **Audit** and **CEO** sign in separately and approve in that order. Comments, evidence, identities, UTC times and revisions remain in history.
7. On rejection, Programme Admin corrects with a reason; Payment resubmits a new revision and all three reviews restart.
8. Once **Fully verified**, Programme Admin exports **Beneficiaries (.xls)** and verifies the worksheet. Two beneficiaries at NGN 25,000 each must total NGN 50,000.

The recorded November dates and IDs are examples. Use destination-appropriate closed registration dates and newly created records. Approval state and beneficiary data live in the backend, not browser local storage. [Complete walkthrough and role matrix](docs/current/USAGE.md).

## Update, troubleshoot and recover

Before updating an existing machine, back up database/filestore and service/deployment configuration, review `git diff` and release hashes, and stage a new source tree. Run `git pull --ff-only` in a clean checkout; rebuild the changed frontends and deliberately apply only their corresponding backend/adapter updates. A pull does not deploy code or migrate operational state.

If a list remains Pending, check Odoo scheduled actions and list errors before retrying; the native worker normally processes once a minute. For a 403, check the authenticated role, programme membership, Origin and cookie/session. For Registry utility failures, check IAM permissions, `NSIPA_REGISTRATION_URL`, CA trust and the private ODK setup. Inspect service logs privately.

Frontend rollback uses the prior release symlink and validated Nginx config. Backend rollback requires the matching private database/filestore and deployment recovery point, reconciliation of later writes and a controlled restart. Do not delete audit history or change approval status manually. [Diagnostics and rollback detail](docs/current/INSTALLATION.md#10-destination-acceptance-operations-and-rollback).

## Verification and limits

The Registry frontend source/lockfile now pins Next.js **16.4.6** and React/React DOM **19.2.7**. The observed runtime inventory remains a record of the original installation; build the new image from this source before deploying the updated frontend.

Release verification covers source integrity, secret-pattern checks, helper plan/configuration behavior, Python syntax, native addon XML, and frontend builds. The original deployed environment exercised native Registry reviews and the five-account PBMS workflow, corrections and binary XLS output. This release has **not** had a complete clean-machine replay. Destination-specific acceptance is required; this README does not claim unattended installation, live-bank settlement, national-identity verification or production acceptance.

Runtime records/secrets and recording media remain outside Git. Third-party components keep their own licenses/notices, including the LGPL-3 declaration of the native addon. Public repository visibility does not grant a new blanket license over every project document or asset. Historical packages are retained with their earlier contents and limits.
