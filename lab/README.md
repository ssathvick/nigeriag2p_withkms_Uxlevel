# Nigeria OpenG2P local UX lab

## Operational and knowledge analytics

Open [Analytics](https://nigeriag2p.com/registration/analytics) with an assigned staff role for current workflow counts, connected OpenG2P summaries, knowledge publishing metrics and library usage. Backend reporting refreshes every 15 minutes through dedicated read-only identities. The [Superset dashboard](https://superset.nigeriag2p.com/superset/dashboard/nigeria-platform-analytics/) uses a separate aggregate reporting database and existing Superset permissions. See [Analytics operations](Analytics-Operations.md) for definitions, scope, retention, verification and recovery. Confirmed settlement and contextual help usage are not included in this release.

Installed on 3 October 2026 in Ubuntu-22.04 under WSL2. Open the [lab launcher](https://openg2p.localhost).

This is a local development environment with synthetic beneficiaries, programme rules, identity records and financial addresses. It provides working services and demo workflows for exploring and building UI/UX. The existing Hyper-V MOSIP-LAB VM was left untouched.

## Access

Run `Show-LabCredentials.ps1` from this folder in PowerShell to view the generated local password. Credentials and private keys are stored inside WSL at `/opt/openg2p-lab/credentials.yaml` and `/opt/openg2p-lab/tls`, readable by root. Do not share the credentials output or backup files.

| Application | URL | Login |
|---|---|---|
| Launcher | https://openg2p.localhost | No login |
| PBMS 3 | https://pbms.openg2p.localhost/web | `admin@nigeria.openg2p.localhost` |
| Modern registry | https://register.openg2p.localhost | Staff SSO: `admin` |
| Odoo social registry | https://registry.openg2p.localhost/web | `admin@nigeria.openg2p.localhost` |
| Staff application launcher | https://staff-portal.openg2p.localhost | Staff SSO: `admin` |
| Beneficiary portal | https://beneficiary.openg2p-ux.localhost/selfservice | Choose **SIGN IN TO LOCAL DEMO**; username `fatima` |
| Beneficiary programme administration | https://portal-admin.openg2p.localhost/web | `admin@nigeria.openg2p.localhost` |
| Approval workflows | https://awe.openg2p.localhost | Staff SSO |
| Master data | https://master-data-ui.openg2p.localhost | Staff SSO |
| Partner management | https://partner-management.openg2p.localhost | Staff SSO |
| Consent management | https://consent-manager.openg2p.localhost | Staff SSO |
| ODK Central | https://odk.openg2p.localhost | Continue → staff SSO |
| Superset | https://superset.openg2p.localhost | Sign in with Keycloak |
| MinIO console | https://minio.openg2p.localhost | Credentials script |
| Keycloak administration | https://keycloak.openg2p.localhost/admin | `admin`, master realm |
| Kafka console | https://kafka.openg2p.localhost | Staff SSO |
| Bridge API documentation | https://bridge.openg2p.localhost/docs | Signed requests required for transaction APIs |
| SPAR mapper API documentation | https://spar.openg2p.localhost/docs | Signed requests required for mapper APIs |

The demo beneficiary uses the same generated lab password as the administrator. Its separate domain prevents staff and beneficiary cookies from colliding. Its access token lasts one hour; sign in again after expiry. The Windows local machine trusts the lab CA, so normal browser HTTPS access works without bypassing certificate warnings.

## What is installed

K3s, Helm, Istio ingress and Nginx TLS termination run in WSL. There are 68 application Deployments/StatefulSets in the `nigeria` namespace. Persistent volumes use K3s local storage.

| Helm release | Installed chart |
|---|---|
| commons | OpenG2P Commons Base 2.3.3 |
| commons-services | OpenG2P Commons Services 2.3.3 |
| pbms | OpenG2P PBMS 3.0.0 |
| registry | OpenG2P Social Registry 2.0.8 |
| register | OpenG2P Registry 1.2.1 |
| spar | OpenG2P SPAR 1.1.0 |
| bridge | OpenG2P G2P Bridge 3.0.0 |
| pbms-beneficiary-portal | Beneficiary Portal 2.0.2 |
| portal-backend | Odoo 26.2.9 chart, PBMS core image 1.3 |
| example-bank | OpenG2P Example Bank 1.1 |

Supporting services include PostgreSQL, Redis, Kafka, MinIO, Keycloak, IAM, master data, approval workflow engine, partner management, consent management, audit manager, key manager with SoftHSM, eSignet with mock identity, Inji Certify, Artifactory, ODK and Superset. Exact container image digests and source commits are recorded in `installed-versions.json`.

**Version compatibility:** The published beneficiary portal API uses the earlier Odoo programme model (`g2p.program`), while PBMS 3 uses `g2p.program.definition`. The portal therefore has its own compatible Odoo database and programme administration workspace. Its applications do not automatically enter PBMS 3. Both workspaces are available for UX exploration; joining them into one Nigeria implementation requires a version-aligned connector or API migration.

## Verified working journeys

1. Staff SSO → modern registry → browse 12 individuals and six households → open Fatima's detail tabs.
2. Submit a demographic edit from the registry UI → two AWE approval stages → signed callback delivery → registry change request becomes **Approved**. The synthetic middle name is now `UX Demo`.
3. PBMS `NG_LAB_FARMER` → fixture-only eligibility → six enrolled demo records → calculate six benefits of NGN 25,000 → aggregate NGN 150,000 → signed envelope and batch creation in Bridge. The PBMS background batch reports `complete`; this means Bridge accepted the disbursement instructions, not that a bank settled them.
4. Key manager signs SPAR requests → link synthetic accounts → signed mapper resolution succeeds. The Bridge worker's actual SPAR connector was also exercised successfully.
5. Beneficiary local OIDC login as Fatima → discover `Nigeria Household Support — Portal UX Demo` → complete the Form.io application → submit → receive application ID `3102678113`.
6. Staff SSO reaches ODK Central with an administrator account and Superset's workspace.
7. Readiness and HTTPS checks cover all 68 workloads and all 18 launcher links. See `health-report.json` for the latest check.

The modern registry's country labels use State/FCT and LGA. Master data contains all 36 states plus FCT and six demonstration LGAs. `NG01`…`NG37` are local lab codes, not official administrative codes. It is not a complete 774-LGA dataset. Twelve mock identities were seeded. `nigeria-fixtures.json` contains only synthetic data.

## Start, stop and check

From PowerShell:

```powershell
Set-Location H:\Nigeria_Mosip\codex\openg2p-lab
.\Start-Lab.ps1
.\Status-Lab.ps1
```

Allow a few minutes after starting. The start script launches a hidden WSL process to keep the lab alive. Inside WSL, systemd starts K3s/Nginx and refreshes hostname mappings for the current WSL IP. Windows still needs a running WSL session; opening the launcher alone cannot start the cluster.

```powershell
.\Stop-Lab.ps1
```

Stop shuts down the lab's K3s containers and Nginx while preserving databases and volumes. It does not stop the Hyper-V MOSIP VM or other WSL distributions. It may leave Ubuntu itself running with negligible lab workload.

Detailed health check:

```powershell
wsl -d Ubuntu-22.04 -u root -- python3 /mnt/h/Nigeria_Mosip/codex/openg2p-lab/smoke-check.py
```

Diagnostics:

```powershell
wsl -d Ubuntu-22.04 -u root -- kubectl -n nigeria get pods
wsl -d Ubuntu-22.04 -u root -- kubectl -n nigeria logs deploy/pbms-celery-worker --tail=40
```

Some upstream services log connection strings or tokens. Keep diagnostic logs private. Completed installation jobs are expected to remain visible. A superseded failed Keycloak initialization job was archived privately and removed after the clients and roles were repaired.

## Backups and recovery

Run `Backup-Lab.ps1`. It creates a private timestamped directory under `/opt/openg2p-lab/backups` containing:

- `pg_dumpall` exports from commons, PBMS, social registry, example bank and portal backend PostgreSQL servers, using each server's matching client version.
- A Kubernetes manifest containing configuration and Secrets.
- A compressed archive of non-database volumes, chart values, lab credentials and TLS material.

The database exports are consistent per database; there is no coordinated transaction across all five servers. File volumes are copied online. For an exact whole-environment recovery point, stop the lab and export the Ubuntu WSL distribution with `wsl --export Ubuntu-22.04 <backup-path>` from Windows, then start it again. A distribution export includes everything in that Ubuntu installation.

A verified logical backup was created on 3 October. Do not commit or distribute backups. The baseline live Kubernetes configuration is also retained privately at `/opt/openg2p-lab/baseline`.

Recovery should use the recorded image versions, restore the matching PostgreSQL exports and file volumes, then reapply the private baseline configuration and refresh local network mappings. Do not import a database dump over a running, modified lab without first making a new backup. A restore into a separate clean distribution has not been performed.

## UI/UX work

Start with the launcher and the two verified journeys: staff registry editing/approval, and beneficiary application submission. Source checkouts are available here:

- `registry-ui-source`: modern registry Next.js UI.
- `beneficiary-ui-source`: current upstream beneficiary UI.
- `upstream-registry-gen2`: registry backend source.
- `upstream-awe`: approval engine source.
- `upstream-deployment`, `upstream-helm`: deployment/chart references.

These source checkouts are reference/development copies; editing them does not change a running container automatically. Their current branches can differ from the installed image releases. Use the image/source inventory and package manifests when choosing a matching branch. Build a custom image with a distinct tag and update the selected deployment after backing up; do not overwrite the upstream image tag.

The installed beneficiary UI is the upstream baseline, including placeholder cards and some `$` labels. Nigerian content, NGN display, accessibility, visual design and navigation improvements are the next UX work, rather than completed redesigns in this installation.

## Local fixes retained

The setup repaired duplicate Helm resources, initial PostgreSQL passwords, local ingress hosts and routes, internal DNS mappings, TLS trust, IAM registration and application roles. PostgreSQL resources were increased and PBMS Celery concurrency was reduced to two to avoid exhausting database connections.

ConfigMaps mount targeted fixes for missing registry imports/session initialization, portal programme-form column naming, AWE quorum handling after reassignment, Bridge signing-helper initialization and the PBMS-to-Bridge wire-format/JSON-signing mismatch. Request signature checking remains active.

The PBMS demo farmer adapter reads its six fixture records from the PBMS database. It is a working sample adapter; it is not a general live connector from the modern household registry. The placeholder `NG_LAB_HOUSEHOLD` programme needs a household adapter before automated eligibility processing.

Do not rerun bootstrap/seed scripts indiscriminately: some regenerate configuration or replace fixture data. Routine use needs only the Start, Stop, Status and Backup scripts. Do not run a plain `helm upgrade` over this lab: it can remove live compatibility fixes. `reconcile-helm.py` is a preservation post-renderer for the present baseline, not a general upgrade mechanism; it intentionally preserves live workload specs, so a deliberate software upgrade needs review of those specs and fixes.

## Integration boundaries

The Example Bank is installed as a simulator. End-to-end treasury funding, bank settlement, reconciliation, notifications and real payment rails have not been certified by this setup. Bridge acceptance and signed mapper resolution have been verified separately.

Mock identities are local. This installation does not connect to Nigeria NIN/NIMC, a production MOSIP deployment, real banks, SMTP/SMS providers or government systems. eSignet/Inji are present as supporting lab services; production identity issuance and wallet journeys need their own implementation configuration.

This lab has broad administrator permissions and shared demonstration credentials for convenient local exploration. It has not been configured or audited as a production deployment.

## Machine footprint

The host has 128 GB RAM and 24 logical processors. WSL has approximately 62 GiB RAM and 16 GiB swap. With the stack running, WSL used approximately 29 GiB RAM and 53 GB filesystem space; C: had approximately 159 GiB free at the final inspection. The WSL virtual disk is backed by C:, even though source files and scripts are on H:. Monitor C: free space as images, documents and backups grow.

## Upstream references

- [OpenG2P documentation](https://docs.openg2p.org/)
- [OpenG2P PBMS source](https://github.com/OpenG2P/pbms)
- [Registry UI source](https://github.com/OpenG2P/openg2p-registry-gen2-staff-portal-ui)
- [Beneficiary UI source](https://github.com/OpenG2P/openg2p-beneficiary-portal-ui)
- [Approval engine source](https://github.com/OpenG2P/awe)

## Final recovery verification

The lab was stopped with the supplied stop script and restarted. All 68 workloads and 18 HTTPS entry points recovered. The saved registry approval, beneficiary application and signed PBMS-to-Bridge batch were verified after recovery. Backup contents were checked; a full backup restore has not been tested.


## IQS branding

The running interfaces now use IQS branding, with a logo from IQ Systems Solutions' official website. Programme-management and shared login screens have the IQS theme. See [branding/README.md](branding/README.md) for the asset source, implementation and recovery details. Existing service URLs and login usernames remain valid.


## One-click Windows startup

Double-click Start-IQS-Nigeria.bat on your Desktop, or Start-IQS-Lab.bat in this folder. The launcher starts Ubuntu-22.04, K3s, Nginx and the startup network repair; keeps WSL running independently of ChatGPT; waits for workload readiness and all HTTPS entry points; then opens https://openg2p.localhost/. Allow several minutes after a Windows restart and keep the launcher window open until it reports ready. It times out after 20 minutes with diagnostics if startup fails. Existing credentials and data remain valid. No administrator elevation is normally required. Closing ChatGPT or the completed launcher window does not stop the services. This is a manual launcher, not a Windows automatic-start task.

The launcher was tested against the running lab: all 68 workloads and 18 entry points passed, and the browser opened successfully. A new Windows reboot was not performed for this launcher test.


Partner Management authentication repair: PARTNER_MANAGER_AUTH_DEFAULT_ISSUERS now matches the staff realm's public HTTPS issuer. Signature verification, administrator role checks and JWKS validation remain enabled. Verified fresh browser login, Requests and Partners pages on 3 October 2026.


## Partner simulation

The staff simulation console is available at https://nigeriag2p.com/registration/simulation. See [Partner-Simulation.md](Partner-Simulation.md) for scenarios, schemas, isolation, worker operation and current integration limits.

