# OpenG2P Experience Kit v3 — NSIPA edition

A reusable UI, persona UX and knowledge management layer extracted from the NigeriaG2P implementation. Version 0.3.0 (delivery v3) is a starter integration template, not a replacement for OpenG2P services or their authorization.

## Included

- A configurable React persona launcher: citizen, registration officer, verification officer, supervisor and all services.
- A shared navigation bar that can be embedded into existing service screens.
- Responsive styling and screen-sensitive help, including the mobile panel with a fixed, visible close button.
- A searchable knowledge library with 54 starter guides: 48 upstream reference guides and six generic workflow guides.
- Guidance editing, independent review, return with feedback, publication, archive, revision history and restoration. Draft changes preserve the previous published version.
- A separate SQLite knowledge database containing only `km_articles` and `km_history`.
- Configurable service URLs, brand text, help routes, CORS origins and identity roles; Docker and local startup examples.

No beneficiary records, registration database, Nigeria state geometry, payment logic, credentials, live infrastructure configuration or Ollama models are included. The AI integration is outside this extraction. Existing guides are plain text and retain available upstream source attribution.

## Local preview

The compiled React bundle is included. No Node installation is needed just to run it.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install Flask==3.1.3
$env:EXPERIENCE_SECURE_COOKIE='0' # local HTTP preview only
.venv\Scripts\python app.py
```

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
EXPERIENCE_SECURE_COOKIE=0 .venv/bin/python app.py
```

Open `http://127.0.0.1:18110/experience/`. The preview exposes public guidance. Editing remains disabled until a trusted identity gateway is connected; there are no bundled administrator passwords. The service links are disabled placeholders except for the knowledge library.

## Adapt to a deployment

1. Edit `config/deployment.json`: brand name, public HTTPS base URL, URL prefix, installed service links and `enabled` flags.
2. Set the `knowledge_roles` values to roles from that installation's identity provider. Task persona selection only filters navigation; it grants no privileges.
3. Replace example hostnames in `screen_mappings`. Order rules from most specific to least specific. Add explicit screen attributes where possible (see `docs/INTEGRATION.md`). Existing OpenG2P route presets are a starting point and must be checked against the installed release.
4. Add every embedding site's exact HTTPS origin to `allowed_origins`; allow any approved reference host in `reference_hosts`.
5. Connect an authenticated identity gateway, restrict backend access, configure independent editor/reviewer accounts and verify publication before exposing management routes.
6. Review the seed content against local procedures before launch. This kit does not copy Nigeria-specific instructions or live edited articles. Publish local instructions using the knowledge editor.

Read `docs/INTEGRATION.md` for the gateway contract, embed tags, deployment and backup. This adds a shared layer around existing services. Embedded help does not redesign every native service form; deeper UI changes require changes in the relevant application.

## Build and verify

```sh
cd ui
npm ci
npm run build
cd ..
python -m unittest discover -s tests -p 'test_*.py' -v
node tests/context.test.cjs
```

`ui/package-lock.json` fixes the frontend dependency graph. Flask is required for tests. Tests use temporary databases and never write to an installed OpenG2P database. `VALIDATION.json` records the checks performed for this package.

## Structure

| Path | Purpose |
|---|---|
| `app.py` | Standalone service and identity/CSRF adapter |
| `knowledge_management.py` | Extracted knowledge lifecycle |
| `knowledge-seed.json` | Portable starter content |
| `templates/` | Library and editorial screens |
| `ui/src/main.jsx` | React persona launcher source |
| `static/` | Built launcher, styling, help and context matching |
| `config/deployment.json` | Deployment settings |
| `docs/` | Integration, content format and permission matrix |
| `compose.yaml`, `Dockerfile` | Deployment examples |

## Provenance and licenses

The knowledge workflow and help panel were extracted from the local NigeriaG2P source snapshot `49a3f06ac877cafa83f0fade8766e62c178c2de1`. Deployment dependencies were replaced with a standalone adapter. The launcher was rewritten to use configuration instead of fixed Nigeria URLs. This is not an official OpenG2P distribution or certification.

See `THIRD_PARTY_NOTICES.md` and `static/workspace.js.LEGAL.txt` for bundled dependency notices. Source ownership and redistribution permission for project-specific code should follow the originating project's terms; this package does not invent a new license grant.

## NSIPA v2 update — 3 November 2026

The default presentation uses the NSIPA Shared Progress logo, favicon and green/gold palette. Editable Illustrator/SVG/Photoshop sources are in `branding-source/`. This is the demonstration identity proposal used in the Nigeria lab. Technical identifiers, cookies, API routes and upstream attribution remain compatible.

This package is independently runnable. External services remain disabled placeholders until configured for your installation. The full lab gateway and native Keycloak/Odoo branding are maintained in the lab repository, separately from this starter kit.

The v1 package is preserved. See `VALIDATION.json` for checks performed on this edition.

## Version 3 — 4 November 2026

This kit adds a runnable, clearly marked fictional field web preview and a v3 feature guide linked from the persona workspace. The web preview stores a sample draft locally and does not implement supervisor authentication or server sync. `examples/android-field-demo/` includes source, sample XForm, reference geography and the test-signed APK: the PIN is a shared demonstration PIN, not an independent authenticated supervisor. OnePlus sample offline reconnection and ODK receipt were tested in the lab, not this portable installation. Never enter real personal information.

`reference-source/` contains selected UI code and dashboard notes from the lab as implementation references, not drop-in standalone services. The atlas and pilot links are disabled configuration placeholders. Dashboards, verified geographical mappings, actual service access, server-side supervisor authorization and programme/payment integrations require separate deployment and acceptance. Real money is never moved by the Jos demonstration. Geographic measures require source, year, level and classification; keep missing values empty.

Offline reference catalogue: Open Admin Data, Nigeria Administrative Divisions, CC BY 4.0, https://github.com/open-admin-data/nigeria-administrative-divisions, retrieved 4 November 2026. Names and IDs need local validation.
