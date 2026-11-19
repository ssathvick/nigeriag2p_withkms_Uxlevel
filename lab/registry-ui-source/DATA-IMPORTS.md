# Data Imports

Data Imports is available from the Master Beneficiary Registry dashboard and workspace navigation. Operators upload CSV/XLSX or fetch CSV from a configured source. They can review mapped values, edit source values, exclude rows and resolve duplicate keys within a batch. An independent approver can approve the batch or return it with a reason. The operator can then transfer it. Registry administrators can transfer approved files if their native role permits intake edits. The existing Registry registration and deduplication workflow handles downstream record checks and publication.

## Local preview

From the Registry UI directory, run `npm ci` once, then:

```powershell
node tests/data-imports-preview.mjs
```

Open <http://127.0.0.1:3101/preview/sign-in>. The launcher prints the location of the generated credentials file. It creates `operator`, `approver` and `administrator` accounts for the loopback fixture. The preview uses isolated storage in the operating system temporary directory and a mocked Registry/IAM on port 3101. Use synthetic data. A sample CSV is available on the sign-in screen. It has a duplicate, a missing value and a row whose identifier starts with `FAIL-`, which simulates partial ingestion. Use separate browser profiles or sign out to switch roles.

1. As operator, choose **New import**, choose **Sample beneficiary list**, upload the CSV and correct or exclude invalid rows. Send it for approval.
2. As approver, open the batch, return it with a reason or approve it.
3. As operator, reopen the batch, transfer it and refresh the Registry receipt. Browse reconciliation and download the batch audit report.
4. As administrator, open **Sources and mappings** to test or save a new version. **Sample connected source** uses the synthetic source API.

## Staging configuration

- Run on a maintained Node 22+ runtime with `node:sqlite`. Set `DATA_IMPORTS_DB` to an absolute SQLite path in a writable persistent volume, with one Registry UI replica for the feature. The database contains source values for review and needs restricted access, backup and a retention process. The fixture runs on a separate SQLite path.
- Set `DATA_IMPORTS_NATIVE_READ_URL` to a TLS-protected read-only connection to the native Registry PostgreSQL database. Its role needs SELECT on the queue columns used in the receipt query and the import file log's `import_file_id` and `record_number` columns. Confirm the table names and service/widget versions in staging. The bridge reads receipt metadata and row numbers only. Check the read connector and known template against a synthetic batch before enabling the route for production use.
- Set `DATA_IMPORTS_DOCUMENT_REFERENCE=catalog` for Registry deployments that enqueue with the catalog document ID. The read-only database role also needs SELECT on the six columns listed in the native template query for this mode.
- Assign the existing Registry Field Agent, Registry First Reviewer and Registry Administrator roles in IAM. Keep their native permissions in place. Approvers see submitted batches. Operators see their own batches. Administrators see all Data Imports batches and can manage mappings. Native enqueue additionally enforces `intakeSubmission:edit`.
- For a connected source, set `DATA_IMPORTS_CONNECTORS` to a JSON object such as `{"referrals":{"label":"Referral export","url":"https://partner.example/beneficiaries.csv","tokenEnv":"DATA_IMPORTS_CONNECTOR_REFERRALS_TOKEN"}}`. Inject bearer tokens from the server's secret store. Connectors accept a CSV response from an operator-initiated fetch. Use a trusted HTTPS endpoint and route it through the deployment's egress policy. URLs and credentials stay server-side.
- Map input column names to the native CSV data model. Each batch retains its mapping version. The UI validates missing required values and within-batch duplicate keys. Match Registry-defined formats and verify downstream deduplication on the pilot source.
- Check **Needs attention** and **Refresh Registry receipt** for returned, unconfirmed, partial or failed transfers. Safe pre-queue failures can be retried in Data Imports. Native workers own ingestion retries. Ambiguous queue requests reconcile by document ID and cannot be resent through the screen while acceptance is uncertain. A Registry row receipt confirms ingestion into the native pipeline. Use Registration review to follow the resulting registration decisions.
- Scheduling, outbound alerts, live IAM provisioning, and OCR require separate staging configuration or implementation. A text PDF may support structured extraction with its original text layer. Scans and images need OCR plus field review. The current module accepts verified structured input only.

Native contract references

- [OpenG2P enqueue endpoint and permissions](https://github.com/OpenG2P/openg2p-registry-gen2-apis/blob/develop/openg2p-registry-staff-portal-api/src/openg2p_registry_staff_portal_api/controllers/input_mechanism_data_controller.py)
- [OpenG2P CSV import worker and per-row ingestion log](https://github.com/OpenG2P/openg2p-registry-gen2-celery/blob/develop/openg2p-registry-celery-workers/src/openg2p_registry_celery_workers/tasks/import_file_process_worker.py)

## Live pilot

The Registry 1.2.1 catalog uses the logical bucket name data_import_files. MinIO rejects underscores in physical bucket names. The live API and import worker use the [storage compatibility patch](../release/registry-data-imports-minio.patch) to map only this logical bucket to data-import-files, while keeping catalog values and API requests compatible.

The live pilot source is labeled Synthetic Data Imports test only. Its model and intake form have no beneficiary publication mapping. Use only fictional rows with the columns Reference and Test note.

Partner Management approved the internal sender NSIPA-STAFF-PORTAL-IMPORT. The live Registry worker selects it through REGISTRY_CELERY_WORKERS_IMPORT_FILE_SENDER_ID. The synthetic model has a semantic pattern for the native ingestion receipt. It has no transformation template or publication mapping, so the pilot verifies ingestion without creating beneficiary registrations.
