# NigeriaG2P with knowledge management and persona UX

Source snapshot of the NigeriaG2P application customisations: role-based persona
workspaces, site-wide navigation, mobile help, screen/stage-sensitive guidance,
central knowledge management, Nigeria state mapping and local Ollama assistance.

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
