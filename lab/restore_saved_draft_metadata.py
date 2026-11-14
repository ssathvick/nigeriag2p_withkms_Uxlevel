"""Expose preserved legacy draft fields through the additive native schema."""
from test_mbr_db_connection import connect
with connect() as c:
 with c.cursor() as q:
  q.execute("UPDATE g2p_intake_form_households h SET sponsor_name=COALESCE(h.sponsor_name,a.original_record->'payload'->>'sponsor'),survey_community=COALESCE(h.survey_community,a.original_record->'payload'->>'community') FROM g2p_native_workflow_legacy_drafts a WHERE h.submission_id=a.submission_id AND EXISTS(SELECT 1 FROM g2p_intake_form_submissions s WHERE s.submission_id=h.submission_id AND s.draft_status='DRAFT')")
  print('Preserved draft metadata exposed in native fields:',q.rowcount)
 c.commit()
