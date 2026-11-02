# NigeriaG2P with knowledge management and persona UX

Source snapshot of the NigeriaG2P application customisations: role-based persona
workspaces, site-wide navigation, mobile help, screen/stage-sensitive guidance,
central knowledge management, Nigeria state mapping and local Ollama assistance.

## Reusable UI, UX and knowledge management template

The separately installable **[OpenG2P Experience Kit](experience-kit/README.md)**
provides a React persona launcher, shared navigation, mobile screen-sensitive
help, and a versioned knowledge library with independent review and publication.
It runs as a separate service and does not connect to beneficiary databases.

**[Download the ready-to-run starter ZIP](downloads/OpenG2P-Experience-Kit-v0.1.0.zip?raw=true)**
or clone this repository and open `experience-kit/`:

```sh
git clone https://github.com/ssathvick/nigeriag2p_withkms_Uxlevel.git
cd nigeriag2p_withkms_Uxlevel/experience-kit
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
EXPERIENCE_SECURE_COOKIE=0 .venv/bin/python app.py
```

Open `http://127.0.0.1:18110/experience/` for a local preview. See the
[kit README](experience-kit/README.md) for Windows instructions and the
[integration guide](experience-kit/docs/INTEGRATION.md) for deployment URLs,
identity roles, embedded help, HTTPS, Docker, backups and production setup.
Service placeholders are disabled by default; configure them for the target
OpenG2P installation. The template has isolated tests but has not yet been
validated against a second OpenG2P installation.

Repository access requires authorization while this repository remains private.

## Included

* `lab/registration_app.py` and related modules: household registration and workflows.
* `lab/registration-ui/`: registration, geography, knowledge and AI templates.
* `lab/persona-ui/`, `lab/registry-ui-source/`, `lab/beneficiary-ui-source/`: frontend sources and dependency locks.
* `lab/knowledge/`: contextual help, published guidance seeds, source mappings and content tooling.
* `lab/local_ai.py`, `lab/ai/`: local knowledge chat and staff guidance drafting.
* `lab/sitewide-ui/`, `lab/branding/`: shared UX and branding.
* `lab/install-*.py`: retained deployment scripts. Review paths and dependencies before using on another machine.
* `UPSTREAM-SOURCES.json` and `lab/installed-versions.json`: upstream references.

## Development and recovery

The deployed environment is Windows WSL2 Ubuntu 22.04, K3s, PostgreSQL, Nginx,
Flask and the installed upstream services. Local AI uses Ollama and qwen3:8b.
React is used in the frontend modules that include React in their package manifests;
the entire platform is not a single React application.

Use each frontend's lock file with `npm ci` to recover omitted dependencies, then
its package build scripts. Python requirements are in `lab/registration-requirements.txt`.
Deployment scripts currently reference the original lab paths and configured domain.
This source snapshot is not a tested unattended clean-machine installer.

Runtime passwords, OIDC secrets, private keys, household databases and backups
are excluded. Configure new secrets on a fresh installation, or recover the exact
running installation using the separately encrypted WSL/data backup.
The original upstream components retain their own licenses; no new blanket license
is granted for project customisations or documents.

## NSIPA branding update

The current lab sources include the NSIPA identity, shared service theme and native company/realm branding installers. See [lab/branding/README.md](lab/branding/README.md) for build, application and verification steps, and editable Illustrator/SVG/Photoshop masters. Historical recovery archives retain their original contents; apply the current branding sources after restoration.
