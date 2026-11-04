"""Scheduled read only backend summaries and a separate aggregate reporting database."""
import json
from pathlib import Path
import psycopg2
from service_reporting import SPECS,view_name

# Fixed aggregate SQL. No demographic fields, beneficiary identifiers or bank details.
SOURCES = {
 'Modern registry': ('register', {
  'registry_records': "SELECT 'Individual records',COUNT(*) FROM g2p_register_individuals UNION ALL SELECT 'Household records',COUNT(*) FROM g2p_register_households",
  'change_request_status': "SELECT COALESCE(approval_status,'Unknown'),COUNT(*) FROM g2p_register_change_requests GROUP BY 1"}),
 'PBMS': ('pbmsdb', {
  'programme_status': "SELECT COALESCE(program_status,'Unknown'),COUNT(*) FROM g2p_program_definition GROUP BY 1",
  'beneficiary_list_workflow': "SELECT COALESCE(list_workflow_status,'Unknown'),COUNT(*) FROM g2p_beneficiary_list GROUP BY 1",
  'benefit_calculation_process': "SELECT COALESCE(entitlement_process_status,'Unknown'),COUNT(*) FROM g2p_beneficiary_list GROUP BY 1",
  'bridge_instruction_process': "SELECT COALESCE(disbursement_batch_creation_status,'Unknown'),COUNT(*) FROM g2p_beneficiary_list GROUP BY 1"}),
 'Approval workflows': ('awe', {
  'request_status': "SELECT COALESCE(status,'Unknown'),COUNT(*) FROM approval_request GROUP BY 1",
  'completed_turnaround_hours': "SELECT 'Median completed request hours',percentile_cont(0.5) WITHIN GROUP (ORDER BY extract(epoch FROM (completed_at-created_at))/3600) FROM approval_request WHERE completed_at>=created_at UNION ALL SELECT '90th percentile completed request hours',percentile_cont(0.9) WITHIN GROUP (ORDER BY extract(epoch FROM (completed_at-created_at))/3600) FROM approval_request WHERE completed_at>=created_at"}),
 'Bridge': ('bridge_db', {
  'instructions': "SELECT 'Disbursement instruction records',COUNT(*) FROM disbursements UNION ALL SELECT 'Reconciliation records not validated as settlement',COUNT(*) FROM disbursement_recons",
  'bank_dispatch_status': "SELECT COALESCE(sponsor_bank_dispatch_status,'Unknown'),COUNT(*) FROM disbursement_batch_control GROUP BY 1"})}


for service,spec in SPECS.items():
    SOURCES[spec['source']]=(spec['database'],{name:'SELECT label,value FROM nsipa_reporting.'+view_name(service,name) for name in spec['metrics']})

def refresh(r):
    config=json.loads((r.ROOT/'analytics-connections.json').read_text())
    results={}
    for source,(database,queries) in SOURCES.items():
        now=r.stamp()
        try:
            with psycopg2.connect(**config['sources'][database], connect_timeout=8) as conn:
                conn.set_session(readonly=True)
                with conn.cursor() as cur:
                    cur.execute("SET LOCAL statement_timeout='10s'")
                    payload={}
                    for name,query in queries.items():
                        cur.execute(query)
                        payload[name]=[{'label':label,'value':float(value) if value is not None else None} for label,value in cur.fetchall()]
            with r.db() as c:
                c.execute('''INSERT INTO analytics_source_cache VALUES(?,?,?,?,NULL)
                    ON CONFLICT(source) DO UPDATE SET refreshed_at=excluded.refreshed_at,payload=excluded.payload,last_attempt=excluded.last_attempt,error=NULL''',
                          (source,now,json.dumps(payload),now))
            results[source]='ok'
        except Exception:
            # Error details can contain connection information; the UI gets only a failure flag.
            with r.db() as c:
                c.execute('''INSERT INTO analytics_source_cache VALUES(?,?,?,?,'refresh_failed')
                    ON CONFLICT(source) DO UPDATE SET last_attempt=excluded.last_attempt,error='refresh_failed' ''', (source,'','{}',now))
            results[source]='failed'
    ops=r.analytics_snapshot()
    # This reporting database holds aggregates only, and is independent of transactional tables.
    with psycopg2.connect(**config['reporting'],connect_timeout=8) as conn, conn.cursor() as cur:
        cur.execute("SET LOCAL statement_timeout='20s'")
        cur.execute('DELETE FROM aggregate_metrics')
        for source in r.rows('SELECT * FROM analytics_source_cache'):
            # Supervisor-only reports stay behind the dashboard role check, not the broader Superset dataset.
            if any(spec.get('restricted') and spec['source']==source['source'] for spec in SPECS.values()):continue
            for metric,rows in json.loads(source['payload']).items():
                for row in rows:
                    cur.execute('INSERT INTO aggregate_metrics VALUES(%s,%s,%s,%s,%s,%s)',
                                (source['source'],metric,row['label'],row['value'],source['refreshed_at'] or None,bool(source['error'])))
        for key,value in ops.items():
            if isinstance(value,(int,float)):
                cur.execute('INSERT INTO aggregate_metrics VALUES(%s,%s,%s,%s,%s,false)',('Intake',key,key,value,r.stamp()))
        cur.execute('DELETE FROM knowledge_daily_usage')
        for row in r.rows('SELECT * FROM analytics_daily_usage'):
            cur.execute('INSERT INTO knowledge_daily_usage VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',tuple(row.values()))
        cur.execute('DELETE FROM knowledge_governance')
        # Export only aggregate editorial state and public availability, not drafts or actors.
        for row in r.rows("SELECT module,status,COUNT(*) AS articles,SUM(CASE WHEN published IS NOT NULL AND status!='archived' THEN 1 ELSE 0 END) AS live FROM km_articles GROUP BY module,status"):
            cur.execute('INSERT INTO knowledge_governance VALUES(%s,%s,%s,%s,%s)',(row['module'],row['status'],row['articles'],row['live'],r.stamp()))
    return results

if __name__=='__main__':
    import registration_app as r
    results=refresh(r)
    print(json.dumps(results))
    if any(v!='ok' for v in results.values()):raise SystemExit(1)
