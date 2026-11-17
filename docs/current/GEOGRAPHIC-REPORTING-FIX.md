# Geographic reporting refresh repair — 17 November 2026

The geographic source in the scheduled aggregate collector failed with SQLSTATE 42501: permission denied for the geography catalogue. The aggregate reporting views depended on the native `ng2p_record_geography` invoker-security view, which correctly retains record-level application protection. Granting the reporting role broad underlying-table access is not the repair.

## Change and scope

`geographic_reporting.py` defines a fixed, no-argument `nsipa_reporting.geography_record_counts()` function. It returns record type, zone/state names, record counts and coordinate-presence counts only. It is SQL/STABLE/SECURITY DEFINER with its search path locked to `pg_catalog` and its source view fully qualified. PUBLIC execution is revoked; the existing `g2p_analytics_reader` receives only function execution. No raw-table grants, registry row-policy changes, record writes, role/password updates, approval actions or payment dispatches are performed.

The three existing security-barrier reporting views retain the same `label,value` output and existing access grants. Their fixed queries now use this aggregate function. Geography reporting remains behind the existing supervisor/intake-reviewer dashboard checks, and these restricted metrics remain excluded from the broader Superset export. Registry records are not confirmed programme recipients, and coordinate presence is not verified GPS accuracy.

The full source provisioner creates the function before these views so a later deployment does not restore the failing dependency. Do not rerun that broad fixture/provisioning script solely to repair an existing system; use the narrow helper below.

## Existing-installation update

Stage source using the existing destination preparation procedure, then inspect the plan:

```bash
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/repair_geographic_reporting.py"
sudo /opt/openg2p-lab/registration-venv/bin/python "$SOURCE/release/repair_geographic_reporting.py" --apply
sudo systemctl start iqs-analytics.service
sudo systemctl show iqs-analytics.service -p Result -p ExecMainStatus
sudo systemctl is-active iqs-analytics.timer
```

The helper supports destination namespace/database/service/secret parameters; inspect `--help`. Apply requires existing geography views, all three reporting views, the existing reporting role and operator access to the PostgreSQL administrator secret. It saves the previous reporting view/function definitions and native security settings in a private mode-0700 recovery directory, then changes only the fixed aggregate function and three views in one database transaction. No credentials are printed. The default is a non-mutating plan that does not contact Kubernetes or read secrets.

The source must include both `geographic_reporting.py` and the updated `service_reporting.py`. The normal full source provisioner also imports this helper. No database/WSL shutdown, application restart, additional package or unrelated module reinstall is required for this repair. The existing collector reads the same reporting view names and cache contract; its existing 15-minute timer continues normally.

## Validation

On the original lab, all three geography metrics reconcile to the protected source view, cached geography data refreshes without error, and all 15 reporting sources are healthy. The reporting identity and Superset identity remain read-only/non-superuser. The reporting identity still cannot read the raw geography catalogue or write registry records. The aggregate function is not executable by PUBLIC. Native invoker options and the registry policy count are unchanged; anonymous reporting endpoints still return HTTP 401.

PBMS programme-map permissions/totals and the existing reconciled simulator payment report passed read-only regression checks. No new payment was dispatched. The helper plan is validated in both source repositories; destination apply and acceptance remain operator steps. See the [sanitized verification summary](../../source-snapshots/2026-11-17-geographic-reporting-fix/verification-summary.json).

For recovery, use the private pre-change reporting-schema definitions with an authorized database administrator, retaining existing owners/ACLs. Restore reporting objects only after reviewing the failed migration; do not roll back registry data, weaken row security or clear payment state. An unsuccessful transaction leaves the previous reporting objects intact.
