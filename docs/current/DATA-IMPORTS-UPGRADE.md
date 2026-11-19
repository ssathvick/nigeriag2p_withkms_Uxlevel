# Enable Data Imports on an existing Registry

Use this guide on a working Master Beneficiary Registry with staff sign-in. A successful acceptance run uploads three fictional rows, excludes one duplicate, obtains independent approval and receives confirmation that the Registry ingested the other two. Run it first against a destination-owned test register or a test intake model with beneficiary publication disabled. For a new installation, complete the Registry and IAM stages in the [current installation guide](INSTALLATION.md) first.

## 1. Identify the deployment and build the update

From a clean client checkout on `main`, run the commands below in Bash. Use the destination namespace and UI deployment if they differ. The image must include the service's existing domain adaptations and build-time settings. Use your existing release process to carry those forward. The application code is in [Registry UI](../../lab/registry-ui-source/).

```bash
set -euo pipefail
git pull --ff-only origin main
git merge-base --is-ancestor 9e390ab HEAD
RELEASE=$(git rev-parse --short=12 HEAD)
LAB="$PWD/lab"
NS=nigeria
UI=register-staff-portal-ui
kubectl config current-context
kubectl -n "$NS" get deployment "$UI" -o jsonpath='{range .spec.template.spec.containers[*]}{.name}{"  "}{.image}{"\n"}{end}'
kubectl -n "$NS" get pvc,hpa
```

Record the current UI image, container name, replica count, rollout strategy and release revision (`kubectl -n "$NS" rollout history deployment/"$UI"`). Back up the deployment values privately. If Data Imports already runs here, back up its PVC using a SQLite-consistent backup or a snapshot with the writer stopped. The database stores uploaded values, approvals and receipt history.

If you use hostname substitution, run the source-preparation procedure in section 4 of the [installation guide](INSTALLATION.md) for this commit, choose a new staging directory and set `LAB` to the resulting lab directory. Carry across the site's existing build-time environment through its normal build process. Build from that destination-configured source. The repository's Dockerfile supplies Node 22 and installs the locked dependencies. For a single-node K3s installation using local images:

```bash
IMAGE="nsipa/master-registry:data-imports-$RELEASE"
docker build -f "$LAB/registry-ui-source/Dockerfile.native" -t "$IMAGE" "$LAB/registry-ui-source"
docker save "$IMAGE" | sudo k3s ctr images import -
```

For a multi-node cluster, build and push a versioned image to your registry and use that full image reference below. Confirm all eligible nodes can pull it. The direct entry point is `/en/data-imports` on the destination Registry host. To add the service-directory card, build the destination-adapted `persona-ui` with `npm ci && npm run build` and publish `dist/site.js` with the matching `sitewide-ui/index.html` through the site's existing static release process.

## 2. Prepare native ingestion and read-only receipts

Have the Registry administrator confirm these items before enabling transfers.

- **Intake destination.** For the included CSV, use a dedicated CSV data model with two text fields named `synthetic_reference` and `note`. In Registry configuration, create or select a test intake form and an **Import File** configuration linking the destination register, form and CSV model. Configure the ingestion semantic pattern for that model. Leave beneficiary publication disabled for the test. Keep the template name for step 4.
- **Worker and sender.** Confirm that the destination import worker is processing the native queue and that `REGISTRY_CELERY_WORKERS_IMPORT_FILE_SENDER_ID` resolves to an approved internal sender in that installation. The pilot used `NSIPA-STAFF-PORTAL-IMPORT`. Use the destination's approved sender and keep any existing ingestion routes working.
- **Document storage.** The Registry 1.2.1 pilot uses catalog document IDs. Its logical bucket is `data_import_files` and its physical MinIO bucket is `data-import-files`. If your 1.2.1 images still pass the underscore name to MinIO, apply the [storage compatibility patch](../../lab/release/registry-data-imports-minio.patch) to the matching Registry core source in **both** the staff API and the import worker. From the source root containing `openg2p_registry_core/`, check with `git apply --check /absolute/path/to/registry-data-imports-minio.patch`, apply it, rebuild the two site images and roll them out using their existing release definitions. If the mapping is already present, retain the working images. Confirm the API can write and the worker can read the same physical bucket.
- **Database access.** Create or reuse a dedicated PostgreSQL login with TLS, CONNECT on the native Registry database and USAGE on its schema. Grant SELECT only on the columns below. Test from the UI's network using the same hostname and CA it will use at runtime. The UI writes its own review state to SQLite.

| Native table | Columns read by Data Imports |
| --- | --- |
| `import_file_process_queue` | `import_file_id`, `intake_form_ingestion_status`, `number_of_records_present`, `number_of_records_ingested`, `intake_form_ingestion_attempts`, `queued_at`, and the installed reference column. The reader uses `document_store_id` if present, otherwise `document_id`. |
| `import_file_process_log` | `import_file_id`, `record_number` |
| `g2p_registry_import_file_configurations` (catalog mode) | `import_file_configuration_id`, `import_file_template_description`, `import_file_template_mnemonic`, `data_model_id`, `form_id`, `register_id` |

## 3. Enable the Registry UI

Use the site's Helm or GitOps values if they own the deployment. The example below shows the equivalent Kubernetes changes for the 1.2.1 catalog installation. Schedule the UI restart. SQLite uses a single writer, so keep one UI replica, use a `Recreate` rollout and reconcile any autoscaler with that setting. An installation that requires multiple active UI replicas needs a different storage arrangement before enabling this version.

1. Provision a filesystem PVC in the UI namespace, writable by the UI container and retained across upgrades. The example calls it `registry-data-imports`. Reuse the original claim for an upgrade. For a new claim on a cluster with a default storage class, the following is an example starting size. Adjust capacity and storage class to the site's retention policy. The volume must support SQLite file locking and its write-ahead log.

   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: registry-data-imports
   spec:
     accessModes: [ReadWriteOnce]
     resources:
       requests:
         storage: 1Gi
   ```

   Save as `imports-pvc.yaml` and run `kubectl -n "$NS" apply -f imports-pvc.yaml`. A storage class using delayed binding can bind when the pod starts.

2. Through your secret manager, create a Secret named `registry-data-imports-reader` in the same namespace with the key `DATA_IMPORTS_NATIVE_READ_URL`. Its value is the read-only PostgreSQL connection URL. Use certificate and hostname verification, and make the issuing CA available to the UI container. For a manual install, supply a private file containing just the URL, without a trailing newline:

   ```bash
   kubectl -n "$NS" create secret generic registry-data-imports-reader \
     --from-file=DATA_IMPORTS_NATIVE_READ_URL=/private/path/registry-read-url
   ```

3. Set `CONTAINER` to the **UI application container** printed in step 1. Keep its existing IAM, backend, gateway, TLS and session settings. The following strategic merge fragment adds the feature to the existing deployment. Set `DATA_IMPORTS_DOCUMENT_REFERENCE` to `catalog` only for a native API that enqueues by `document_id`. For installations that enqueue by `document_store_id`, omit that entry and confirm the variable is unset. Keep local preview mode unset.

   ```bash
   read -r -p 'Registry UI container name: ' CONTAINER
   : "${CONTAINER:?Select the UI container}"
   cat > imports-ui.patch.yaml <<EOF
   spec:
     replicas: 1
     strategy:
       type: Recreate
       rollingUpdate: null
     template:
       spec:
         volumes:
           - name: data-imports
             persistentVolumeClaim:
               claimName: registry-data-imports
         containers:
           - name: $CONTAINER
             image: $IMAGE
             imagePullPolicy: IfNotPresent
             volumeMounts:
               - name: data-imports
                 mountPath: /var/lib/data-imports
             env:
               - name: DATA_IMPORTS_DB
                 value: /var/lib/data-imports/imports.sqlite
               - name: DATA_IMPORTS_DOCUMENT_REFERENCE
                 value: catalog
               - name: DATA_IMPORTS_NATIVE_READ_URL
                 valueFrom:
                   secretKeyRef:
                     name: registry-data-imports-reader
                     key: DATA_IMPORTS_NATIVE_READ_URL
   EOF
   kubectl -n "$NS" patch deployment "$UI" --type=strategic --patch-file imports-ui.patch.yaml --dry-run=server -o name
   kubectl -n "$NS" patch deployment "$UI" --type=strategic --patch-file imports-ui.patch.yaml
   kubectl -n "$NS" rollout status deployment/"$UI" --timeout=240s
   kubectl -n "$NS" exec deployment/"$UI" -c "$CONTAINER" -- node -e \
     'const fs=require("node:fs"); const p=process.env.DATA_IMPORTS_DB; if(!p || !process.env.DATA_IMPORTS_NATIVE_READ_URL) process.exit(1); fs.accessSync(require("node:path").dirname(p),fs.constants.W_OK); require("node:sqlite"); console.log("SQLite available, directory writable, receipt URL configured");'
   ```

4. Assign separate destination staff accounts the native **Registry Field Agent** (operator), **Registry First Reviewer** (approver) and **Registry Administrator** (source setup) roles. Give the operator the native `intakeSubmission:edit` permission for transfer. Sign in again after role changes. Check that each account has one matching Registry scope. Open the Registry dashboard and select **Data Imports**.

## 4. Configure the source and run the acceptance file

Download [data-imports-acceptance.csv](examples/data-imports-acceptance.csv) using **Raw** on GitHub, or take it directly from `docs/current/examples/` in your checkout. It contains a header and three fictional rows.

1. **Administrator.** In **Sources and mappings â†’ Create a source**, name the source `Synthetic acceptance`. Select the test register and native template from step 2. Choose **Upload a file**, enable **Available for new imports**, and add these required mappings. Select `synthetic_reference` for **Field for duplicate checks** and select **Save source mapping**.

   | Spreadsheet column | Registry column | Transform |
   | --- | --- | --- |
   | `Reference` | `synthetic_reference` | Trim and uppercase |
   | `Test note` | `note` | Trim spaces |

2. **Operator.** Open **New import**, choose **Synthetic acceptance**, upload the CSV and select **Validate file**. Expect **3 uploaded, 2 passed, 1 with issues, 0 excluded**. Expand spreadsheet row **3**. Its reference repeats row 2 after mapping to `DEMO-001`.
3. **Operator.** Select **Exclude this row from the transfer** on row 3 and **Save row**. Expect **3 uploaded, 2 passed, 0 with issues, 1 excluded**. Select **Send for approval**. Record the batch identifier or filename and submission time.
4. **Approver.** In a separate session, open **Transfers â†’ Awaiting approval**, select that batch, verify the counts and choose **Approve batch**. The status becomes **Approved**.
5. **Operator.** Reopen the approved batch, select **Transfer to Registry** once, then **Refresh Registry receipt** while the worker processes it. Completion is **Ingested by Registry**, with **2 of 2** ingested and a native receipt ID. The ingested references correspond to `DEMO-001` and `DEMO-002`. The excluded spreadsheet row stays visible in reconciliation.
6. **Acceptance evidence.** Select **Download audit report** and retain the JSON privately with the deployed commit, batch ID and receipt ID. Reopen the batch from transfer history and verify the same result. For the isolated model, this completes the ingestion test. Beneficiary publication follows the destination's separate registration workflow.

The supplied CSV was exercised through the published application in an isolated preview using separate operator and approver sessions. Its mock Registry returned a receipt for two of two rows. Repeat steps 1–6 on the client installation to verify its native catalog, object storage, PostgreSQL reader and worker.

## Troubleshooting and rollback

| Symptom | Check or action |
| --- | --- |
| Data Imports is missing, returns 403 or shows unavailable | Check the UI image, a fresh sign-in, one supported native role, and `DATA_IMPORTS_DB` on the running UI container. Check mount permissions and PVC binding. |
| No native template appears | Confirm the selected register, test intake form and CSV model are linked by a native Import File configuration. In catalog mode, verify the read role can query the six template columns. |
| Upload works but transfer fails before queuing | Check native intake edit permission, the document reference mode and API/worker MinIO mapping. Use **Retry transfer** only when the batch offers it. |
| Queued, unconfirmed or partially ingested | Refresh the existing receipt. Check the reader's TLS trust, schema/search path, column access, worker health, sender and semantic pattern. Match native logs to the batch's document or receipt ID. Resolve an uncertain submission before sending another file. |
| Batch history disappears after a restart | Verify the same PVC is mounted at the same path and only one UI writer is active. Stop new imports until the original database is identified. |

To roll back, stop new submissions and record any queued or unconfirmed IDs for reconciliation. Restore the previous UI release **and deployment values** from step 1, including replica count and rollout strategy. Restore the previous service-directory assets if updated. Retain the SQLite PVC, audit history and native receipts. Reconcile outstanding native jobs before reverting any worker or storage compatibility changes. Verify staff sign-in and the pre-upgrade Registry workflow after rollback.

The [module reference](../../lab/registry-ui-source/DATA-IMPORTS.md) covers optional connected CSV sources and the separate loopback preview.
