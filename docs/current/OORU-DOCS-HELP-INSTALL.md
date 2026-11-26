# Install NSIPA documentation and contextual Help on Ooru

This release packages 29 service chapters and 568 public Knowledge Library entries, including 295 contextual workflow, screen and field guides. The published sandbox demonstrates the intended navigation and guidance. [NSIPA documentation](https://docs.g2p.wverve.in/)

| Checkout | Set `LAB` to | Use it for |
| --- | --- | --- |
| `ssathvick/iqs-nigeria-g2p` | `$PWD/latest-source/lab` | Base installation and the current application overlay |
| `ssathvick/nigeriag2p_withkms_Uxlevel` | `$PWD/lab` | The same docs and Help package in the UX/KMS application tree |

Use one checkout for a deployment. The package supplies the static docs, published guidance, Knowledge Library code and Help assets. The existing application installation owns Registry and PBMS data, native jobs, user identities and permissions. Follow the matching prerequisite guides for those services. [Base and overlay installation](INSTALLATION.md) · [Data Imports upgrade](DATA-IMPORTS-UPGRADE.md) · [PBMS payments](PBMS-PAYMENTS.md)

## 1. Build a release for the destination

Use Python 3.10 or newer. Run the portal builder with the registration virtual environment, which provides Flask for the shared KMS modules. Run the commands from the chosen repository root in Bash. Set up the destination DNS, TLS, platform host and service hostnames. The example assumes one HTTPS host per service and the registration gateway at `/registration`. If Ooru shares one host across services, adapt the Help service selection to use its route prefixes and verify the result on every affected service before publishing it.

```bash
LAB="$PWD/lab"                         # UX/KMS checkout
# LAB="$PWD/latest-source/lab"         # IQS checkout
CONFIG="$HOME/nsipa-docs-help.local.json"
RELEASE_ROOT=/srv/nsipa-knowledge
RELEASE="$RELEASE_ROOT/releases/$(git rev-parse --short=12 HEAD)"
cp "$LAB/release/docs-help.example.json" "$CONFIG"
```

Replace the example hostnames and set `registration_upstream` to the registration gateway origin reachable from the reverse proxy. The example uses a loopback upstream. Keep this config outside Git. Use private network routing for internal HTTP and configure TLS verification at the proxy for any HTTPS upstream.

```bash
python3 "$LAB/release/prepare_docs_help.py" --config "$CONFIG" --output "$RELEASE"
DOCS_HOST=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["docs"])' "$CONFIG")
PLATFORM_HOST=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["platform"])' "$CONFIG")
"${REGISTRATION_PYTHON:-/opt/openg2p-lab/registration-venv/bin/python}" "$RELEASE/source/platform-docs/build.py" "$RELEASE/site" \
  --prefix '' --origin "https://$DOCS_HOST"
```

The deployment account needs write access to the release directory and Nginx needs read access. Use a new release directory for each build. The seed build should report 29 chapters, 295 contextual topics, 273 additional library topics and 598 pages including the home page. The builder checks that every included guide has its source text, navigation entry, search result and canonical URL. It also checks internal links, anchors and the sitemap.

## 2. Install or upgrade the Knowledge Library

The 23 November Registry update includes 34 new articles and revised Help scripts. On an existing installation, merge the seed in this section, rebuild the published docs and install the versioned Help tags in section 3. Verify the dashboard, approval queue and mobile checks in section 4. [Registry help audit](MASTER-REGISTRY-HELP-AUDIT.md)

**For a visual-only update on an existing installation**, stage the new release as in section 1. Continue with the published-feed build and docs root in section 3. The existing Knowledge Library and Help integration can serve this update without a database merge or registration-service restart. Keep the current Help assets available if the release pointer also serves them.

The 25 November update changes Help routing, the editor, source visibility and the documentation build. Preserve the existing seed and database. Use the updated Help tags and rebuild the public site from the anonymous feed. The [authoring pilot](KMS-AUTHORING-PILOT.md) records the 15 reviewed examples.

On a fresh installation, deploy `registration/knowledge_management.py`, `registration/km_governance.py`, `registration/knowledge-seed.json` and the staged `registration/local_ai.py`, `registration/static/local-ai.js` and four `registration/templates/knowledge-*.html` files with the existing registration service. The registration app calls `knowledge_management.install(...)` during startup. It creates the Knowledge Library tables and seeds the release. Preserve the destination's `base.html`, remaining library templates, identity settings and application configuration.

On an existing installation, preview the merge. The runtime paths below are from the base installation. Adjust them for Ooru before running the commands.

```bash
REG=/opt/openg2p-lab/registration
PYTHON=/opt/openg2p-lab/registration-venv/bin/python
KM_SERVICE=iqs-registration.service
sudo "$PYTHON" "$LAB/release/merge_knowledge.py" \
  --database "$REG/intake.sqlite" --seed "$RELEASE/registration/knowledge-seed.json"
```

The preview reports inserts, updates, unchanged entries and preserved entries. The merge updates published system-owned entries by stable slug and records a new version in the existing history. Drafts, staff-only content, archived entries and staff edits retain their state. Resolve a context-key collision using the library's editorial process before applying the upgrade.

Schedule a maintenance window for the registration gateway. Stop its writers, then back up the installed files and the database. Use a new private backup directory.

```bash
BACKUP="/var/backups/nsipa-knowledge/$(date -u +%Y%m%dT%H%M%SZ)"
sudo install -d -m 0700 "$BACKUP"
sudo systemctl stop "$KM_SERVICE"
sudo cp -a "$REG/knowledge_management.py" "$REG/knowledge-seed.json" "$REG/local_ai.py" "$REG/static/local-ai.js" \
  "$REG/templates/knowledge-article.html" "$REG/templates/knowledge-library.html" \
  "$REG/templates/knowledge-editor.html" "$REG/templates/knowledge-revision.html" "$REG/templates/knowledge-admin.html" "$BACKUP/"
for F in "$REG/km_governance.py" "$REG/templates/knowledge-register.html" "$REG/templates/knowledge-checks.html"; do
  if [ -f "$F" ]; then sudo cp -a "$F" "$BACKUP/"; fi
done
sudo "$PYTHON" "$LAB/release/merge_knowledge.py" \
  --database "$REG/intake.sqlite" --seed "$RELEASE/registration/knowledge-seed.json" \
  --apply --backup "$BACKUP/intake.sqlite"
sudo install -m 0644 "$RELEASE/registration/km_governance.py" "$RELEASE/registration/knowledge_management.py" \
  "$RELEASE/registration/knowledge-seed.json" "$RELEASE/registration/local_ai.py" "$REG/"
sudo install -m 0644 "$RELEASE/registration/static/local-ai.js" "$REG/static/"
sudo install -m 0644 "$RELEASE/registration/templates/"knowledge-*.html "$REG/templates/"
sudo systemctl start "$KM_SERVICE"
curl --fail --silent --show-error "https://$PLATFORM_HOST/registration/health"
```

Run the preview again before resuming publishing work. A repeated merge of the same release should report no inserts or updates. Confirm that the anonymous API exposes public guidance and that the signed-in library still enforces access to staff-only articles. The docs and Help work with published guidance and have no model dependency.

## 3. Publish the docs and wire Help into the service layouts

For an existing deployment, build from the destination's anonymous published feed after upgrading the library. This includes approved local revisions and reuses the destination's article IDs. Run the following into a new site directory inside the release. Review a missing contextual article with the library owner and preserve its visibility settings.

```bash
PUBLISHED=$(mktemp)
curl -q --fail --silent --show-error \
  "https://$PLATFORM_HOST/registration/api/knowledge?include_roles=1" > "$PUBLISHED"
"${REGISTRATION_PYTHON:-/opt/openg2p-lab/registration-venv/bin/python}" "$RELEASE/source/platform-docs/build.py" "$RELEASE/published-site" \
  --prefix '' --origin "https://$DOCS_HOST" --knowledge-file "$PUBLISHED"
```

Point the docs virtual host, ingress or static publisher at the verified build. Serve directory indexes at routes such as `/data-imports/` and `/topics/imports/receipt-log-restored/`. The checked-in publisher inputs work with a standard static host. Use a separate docs route or virtual host to serve the docs' own assets. If using Nginx, set the document root to the chosen build, `index index.html;` and `try_files $uri $uri/ =404;` in the site location. Add TLS using Ooru's existing certificate and ingress process.

Point `/srv/nsipa-knowledge/current` at the verified release. Run the following as the release owner. Retain the previous target for rollback.

```bash
readlink "$RELEASE_ROOT/current" || true
NEXT="$RELEASE_ROOT/.current-$(basename "$RELEASE")"
ln -s "$RELEASE" "$NEXT"
mv -Tf -- "$NEXT" "$RELEASE_ROOT/current"
```

Point the docs root at `current/published-site` when you built from the public feed, or `current/site` when using the seed build. In each service that renders the Help panel:

1. Mount the staged `help/` directory at `/iqs-brand/docs-help/`. Include the generated `nginx-help.conf` in that service's proxy or implement both routes in its ingress. Replace any existing exact `/iqs-brand/knowledge` location with the generated proxy. It forwards only anonymous requests to the public feed, strips cookies and authorization headers, and suppresses upstream cookie headers.
2. Add the generated `help-tags.html` tags to the existing server-rendered layout or application template. Use the config, context resolver and Help scripts in that order. Replace the equivalent older tags to keep one Help launcher. Rebuild or roll out applications that package the layout into an image.
3. Add a **Documentation** link to `https://$DOCS_HOST/` in the platform navigation. Map service links to the destination domains used in step 1. Ensure the Registry's native `/api/me` returns the signed-in `registry_scope` and the PBMS integration exposes `nsipa_identity` through its existing Odoo session. The Help role selection follows those endpoints and rendered screen markers. The protected workflow actions still enforce their own permissions.
4. Validate and reload the proxy with `nginx -t` and the deployment's normal reload process. Use a fresh browser session to verify the asset version, the Help launcher and the Documentation link. Confirm that the site stylesheet and scripts load without 404s.

## 4. Verify in staging

Open the household registration and restored-receipt guides on a phone. Check that the process diagram stacks, the screenshot opens at full size and closing it returns to the same instruction. Confirm the static host serves the WebP files under `assets/visuals/` with the `image/webp` content type. The maintainer guide includes the example routes, a local preview command and the screenshot placement format. [Visual guide maintenance](../../lab/platform-docs/README.md)

Run the source catalog checks with Node.js and verify the deployed routes using destination-owned synthetic records.

```bash
node "$LAB/knowledge/test-contextual-rebuild.cjs"
curl --fail --silent --show-error -o /dev/null "https://$DOCS_HOST/search.json"
curl --fail --silent --show-error -o /dev/null \
  "https://$DOCS_HOST/topics/imports/receipt-log-restored/"
```

| Area | Expected result |
| --- | --- |
| Docs and library | Search lands on the expected workflow or role guide. Service links use destination hosts. Upstream articles are labelled as references. Published docs open the matching Knowledge Library article. Staff-only test guidance requires authorised access and stays out of public search. |
| Master Registry | Check the Field Agent, First Reviewer, Second Reviewer, MBR Officer and Registry Administrator accounts. Wherever the **Form submissions** card is visible, its information button opens **Registration review queues**. An empty registration approval queue opens **My registration reviews**. With an open or claimed task, First Reviewer and Second Reviewer receive their respective level-specific guides. On a restricted page, Help explains how to request access. On a phone, open a section or field guide and check that **Open documentation guide** opens the same topic on the destination docs host. Verify returned records, review queues and both duplicate tabs. Check that each match appears once per tab in a release with the current Registry matcher. |
| Data Imports and Data Bridge | Verify connected CSV failure and retry, one draft per retry, independent approval and receipts. For a partial receipt, correct only the outstanding row. Where native saved-row tracking and receipt recovery are installed, confirm that restored receipts keep one saved row and one receipt log, including overlapping late deliveries, and that a matching alternate remains blocked. Verify that Help opens the matching documentation for Field Agent, First Reviewer and Registry Administrator. Second Reviewer sees the access guide. |
| PBMS and Bridge | Verify the installed revision of the Programme Admin, Payment, Finance, Audit and CEO flow. Check resubmission, partial payments, reversal and case closure guidance. Where the matching Bridge reconciliation update is installed, distinguish repeated reversals from a different-amount exception across bank statements. |

The published guides for connected CSV concurrency, saved-row receipt recovery and later reversal scenarios describe the corresponding sandbox application revisions. The docs and Help release does not install those native worker, Registry, PBMS or Bridge changes. Compare Ooru's application revision and UI state markers with the scenarios above before treating those guides as operational instructions. Use the service owner to resolve any implementation difference.

## 5. Roll back or publish a later revision

For a docs or Help asset rollback, point `current` and the docs root at their previous verified release and restore the previous layout tags and proxy configuration. Validate and reload. For a Knowledge Library rollback during the maintenance window, stop the registration service, restore the backed-up code, static editor script and templates and use SQLite's backup API to restore the consistent database copy to the stopped database. If writes resumed after the upgrade, reconcile those changes before restoring database state. Confirm sign-in, library access and Help after recovery.

For subsequent content updates, publish the approved article in the Knowledge Library, export the anonymous published feed again, then rebuild, verify and switch the static release. Use a staff review when a source has changed or when a guide's operational status needs approval.
