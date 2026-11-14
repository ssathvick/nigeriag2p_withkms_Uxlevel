"""Generate fail-closed RLS for every native record-bearing table in the release schema."""
from pathlib import Path
import json
root=Path(__file__).parent
schema=json.loads((root/'register-schema.json').read_text())
schema={table:(cols.strip('{}').split(',') if isinstance(cols,str) else cols) for table,cols in schema.items()}
sql=[];tables={}
for table,cols in schema.items():
    if table=='ng2p_record_geography':
        sql.append('ALTER VIEW public.ng2p_record_geography SET (security_invoker=true);')
        continue
    read=None;write='false'
    if table=='g2p_intake_form_submissions':
        read='nsipa_visible_intake(submission_id::text)';write="nsipa_scope()='field' AND nsipa_visible_intake(submission_id::text)"
    elif table.startswith('g2p_intake_form_') and 'submission_id' in cols:
        read='nsipa_visible_intake(submission_id::text)';write='nsipa_editable_intake(submission_id::text)'
        if 'internal_record_id' in cols:
            sql.append(f'DROP TRIGGER IF EXISTS nsipa_capture_origin ON public."{table}"; CREATE TRIGGER nsipa_capture_origin BEFORE INSERT OR UPDATE ON public."{table}" FOR EACH ROW EXECUTE FUNCTION nsipa_capture_record_origin();')
    elif table=='g2p_registry_documents':
        read='nsipa_visible_document(document_id::text)';write='nsipa_editable_document(document_id::text)'
    elif table=='dedup_results_intake_forms_vs_intake_forms':
        read='nsipa_visible_intake(submission_id::text) AND nsipa_visible_intake(candidate_submission_id::text)'
    elif table=='dedup_results_intake_forms_vs_register':
        read='nsipa_visible_intake(submission_id::text) AND nsipa_visible_master(internal_record_id::text)'
    elif 'change_request_id' in cols and table!='g2p_register_section_completion_score':
        read='false'
    elif 'submission_id' in cols:
        read='nsipa_visible_intake(submission_id::text)'
        if table=='g2p_intake_section_documents':write='nsipa_editable_intake(submission_id::text) AND nsipa_visible_document(document_id::text)'
    elif 'internal_record_id' in cols:
        read='nsipa_visible_master(internal_record_id::text)'
    elif 'artifact_id' in cols:
        read='nsipa_visible_intake(artifact_id::text)'
    elif table=='g2p_registry_review_comments':
        read='EXISTS(SELECT 1 FROM awe_req_events e WHERE e.event_id=g2p_registry_review_comments.event_id AND nsipa_visible_intake(e.artifact_id::text))'
    elif table in {'g2p_mbr_source_archive','g2p_mbr_submissions','g2p_mbr_master_data','g2p_mbr_events'}:
        read='false'
    if read is None:continue
    tables[table]={'read':read,'write':write}
    sql.extend([f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY;',
      f'DROP POLICY IF EXISTS nsipa_native_service ON public."{table}";',
      f"CREATE POLICY nsipa_native_service ON public.\"{table}\" FOR ALL TO register_user USING(current_user='register_user') WITH CHECK(current_user='register_user');",
      f'DROP POLICY IF EXISTS nsipa_scope_select ON public."{table}";',
      f'CREATE POLICY nsipa_scope_select ON public."{table}" FOR SELECT TO nsipa_registry_scoped USING ({read});',
      f'DROP POLICY IF EXISTS nsipa_scope_insert ON public."{table}";',
      f'CREATE POLICY nsipa_scope_insert ON public."{table}" FOR INSERT TO nsipa_registry_scoped WITH CHECK ({write});',
      f'DROP POLICY IF EXISTS nsipa_scope_update ON public."{table}";',
      f'CREATE POLICY nsipa_scope_update ON public."{table}" FOR UPDATE TO nsipa_registry_scoped USING ({write}) WITH CHECK ({write});',
      f'DROP POLICY IF EXISTS nsipa_scope_delete ON public."{table}";',
      f'CREATE POLICY nsipa_scope_delete ON public."{table}" FOR DELETE TO nsipa_registry_scoped USING ({write});'])
# Reconciliation may update status summaries, but cannot widen ledger visibility.
sql.append("DROP POLICY IF EXISTS nsipa_scope_reconcile ON public.g2p_intake_form_submissions; CREATE POLICY nsipa_scope_reconcile ON public.g2p_intake_form_submissions FOR UPDATE TO nsipa_registry_scoped USING (nsipa_visible_intake(submission_id::text)) WITH CHECK (nsipa_visible_intake(submission_id::text));")
(root/'policies.sql').write_text('\n'.join(sql)+'\n',encoding='utf-8')
(root/'policy-inventory.json').write_text(json.dumps(tables,indent=2))
print('Scoped record tables:',len(tables))
