CREATE SCHEMA IF NOT EXISTS nsipa_security;
REVOKE ALL ON SCHEMA nsipa_security FROM PUBLIC;
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='nsipa_registry_scoped') THEN
  CREATE ROLE nsipa_registry_scoped NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
 END IF;
END $$;
GRANT nsipa_registry_scoped TO register_user;
GRANT USAGE ON SCHEMA public TO nsipa_registry_scoped;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO nsipa_registry_scoped;
GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO nsipa_registry_scoped;
CREATE TABLE IF NOT EXISTS nsipa_security.intake_owner(
 submission_id text PRIMARY KEY, owner_sub text NOT NULL, owner_name text NOT NULL,
 field_origin boolean NOT NULL, scope_state text NOT NULL DEFAULT 'draft',
 request_id text, last_event_at timestamptz, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS nsipa_security.record_origin(internal_record_id text PRIMARY KEY,submission_id text NOT NULL);
CREATE TABLE IF NOT EXISTS nsipa_security.document_owner(document_id text PRIMARY KEY,owner_sub text NOT NULL);
CREATE TABLE IF NOT EXISTS nsipa_security.field_actors(subject text PRIMARY KEY,username text NOT NULL);
CREATE TABLE IF NOT EXISTS nsipa_security.registry_admins(subject text PRIMARY KEY);
CREATE OR REPLACE FUNCTION public.nsipa_ingest_owner(p_sub text) RETURNS text
LANGUAGE sql SECURITY DEFINER SET search_path=pg_catalog,nsipa_security AS $$
 SELECT username FROM nsipa_security.field_actors WHERE subject=p_sub
$$;

CREATE OR REPLACE FUNCTION public.nsipa_scope() RETURNS text LANGUAGE sql STABLE AS $$
 SELECT COALESCE(NULLIF(current_setting('nsipa.role',true),''),'service')
$$;
CREATE OR REPLACE FUNCTION public.nsipa_visible_intake(p_id text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
 SELECT CASE public.nsipa_scope()
 WHEN 'admin' THEN true
 WHEN 'field' THEN EXISTS(SELECT 1 FROM nsipa_security.intake_owner o WHERE o.submission_id=p_id AND o.owner_sub=current_setting('nsipa.sub',true) AND o.scope_state IN ('draft','level1','returned'))
 WHEN 'level1' THEN EXISTS(SELECT 1 FROM nsipa_security.intake_owner o WHERE o.submission_id=p_id AND o.field_origin AND o.scope_state='level1')
 WHEN 'level2' THEN EXISTS(SELECT 1 FROM nsipa_security.intake_owner o WHERE o.submission_id=p_id AND o.field_origin AND o.scope_state='level2')
 WHEN 'officer' THEN EXISTS(SELECT 1 FROM nsipa_security.intake_owner o WHERE o.submission_id=p_id AND o.field_origin AND o.scope_state='approved')
 ELSE false END
$$;
CREATE OR REPLACE FUNCTION public.nsipa_editable_intake(p_id text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
 SELECT public.nsipa_scope()='field' AND EXISTS(SELECT 1 FROM nsipa_security.intake_owner o WHERE o.submission_id=p_id AND o.owner_sub=current_setting('nsipa.sub',true) AND o.scope_state IN ('draft','returned'))
$$;
CREATE OR REPLACE FUNCTION public.nsipa_visible_master(p_id text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
 SELECT public.nsipa_scope()='admin' OR (public.nsipa_scope()='officer' AND EXISTS(
 SELECT 1 FROM nsipa_security.record_origin r JOIN nsipa_security.intake_owner o USING(submission_id)
 WHERE r.internal_record_id=p_id AND o.field_origin AND o.scope_state='approved'))
$$;
CREATE OR REPLACE FUNCTION public.nsipa_capture_intake_owner() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
DECLARE r text:=public.nsipa_scope();
BEGIN
 IF TG_OP='INSERT' THEN
  IF r='field' THEN
   NEW.created_by:=current_setting('nsipa.name',true);
   INSERT INTO nsipa_security.intake_owner(submission_id,owner_sub,owner_name,field_origin)
   VALUES(NEW.submission_id::text,current_setting('nsipa.sub',true),NEW.created_by,true);
  END IF;
 ELSE
  IF NEW.created_by IS DISTINCT FROM OLD.created_by AND r NOT IN ('service','admin') THEN
   RAISE EXCEPTION 'Submission ownership cannot be changed';
  END IF;
  IF NEW.awe_request_id IS DISTINCT FROM OLD.awe_request_id AND NEW.awe_request_id IS NOT NULL THEN
   UPDATE nsipa_security.intake_owner SET scope_state='level1',request_id=NEW.awe_request_id::text,last_event_at=NULL WHERE submission_id=NEW.submission_id::text;
  END IF;
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS nsipa_capture_owner ON g2p_intake_form_submissions;
CREATE TRIGGER nsipa_capture_owner BEFORE INSERT OR UPDATE ON g2p_intake_form_submissions FOR EACH ROW EXECUTE FUNCTION public.nsipa_capture_intake_owner();

CREATE OR REPLACE FUNCTION public.nsipa_capture_record_origin() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
DECLARE previous text; master_table text; already_master boolean;
BEGIN
 IF NEW.internal_record_id IS NOT NULL THEN
  SELECT submission_id INTO previous FROM nsipa_security.record_origin WHERE internal_record_id=NEW.internal_record_id::text;
  IF public.nsipa_scope()='field' AND previous IS NULL THEN
   master_table:=replace(TG_TABLE_NAME,'g2p_intake_form_','g2p_register_');
   IF to_regclass('public.'||master_table) IS NOT NULL THEN
    EXECUTE format('SELECT EXISTS(SELECT 1 FROM public.%I WHERE internal_record_id::text=$1)',master_table) INTO already_master USING NEW.internal_record_id::text;
    IF already_master THEN RAISE EXCEPTION 'An existing master record cannot be claimed by a new submission'; END IF;
   END IF;
  END IF;
  IF previous IS NOT NULL AND previous<>NEW.submission_id::text AND public.nsipa_scope()='field' THEN
   RAISE EXCEPTION 'This record belongs to another submission';
  END IF;
  INSERT INTO nsipa_security.record_origin(internal_record_id,submission_id) VALUES(NEW.internal_record_id::text,NEW.submission_id::text) ON CONFLICT DO NOTHING;
 END IF;
 IF public.nsipa_scope()='field' THEN NEW.created_by:=current_setting('nsipa.name',true); END IF;
 RETURN NEW;
END $$;

CREATE OR REPLACE FUNCTION public.nsipa_security_decision(p_id text,p_stage integer,p_action text) RETURNS boolean
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
DECLARE expected text;
BEGIN
 expected:=CASE p_stage WHEN 1 THEN 'level1' WHEN 2 THEN 'level2' ELSE 'invalid' END;
 IF public.nsipa_scope()<>expected OR p_action NOT IN ('approve','return','reject') THEN RAISE EXCEPTION 'Review scope mismatch'; END IF;
 UPDATE nsipa_security.intake_owner SET scope_state=CASE p_action WHEN 'return' THEN 'returned' WHEN 'reject' THEN 'rejected' ELSE CASE p_stage WHEN 1 THEN 'level2' ELSE 'approved' END END
 WHERE submission_id=p_id AND field_origin AND scope_state=expected;
 RETURN FOUND;
END $$;

CREATE OR REPLACE FUNCTION public.nsipa_security_event() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
DECLARE next_state text;
BEGIN
 IF NOT NEW.applied OR NEW.artifact_type<>'registry.intake_form' THEN RETURN NEW; END IF;
 next_state:=CASE
 WHEN NEW.event_type='request_rejected' THEN 'rejected'
 WHEN NEW.event_type='request_returned' THEN 'returned'
 WHEN NEW.event_type='request_approved' THEN 'approved'
 WHEN NEW.event_type='stage_started' AND NEW.stage_order=2 THEN 'level2'
 WHEN NEW.event_type='stage_started' AND NEW.stage_order=1 THEN 'level1'
 ELSE NULL END;
 IF next_state IS NOT NULL THEN
  UPDATE nsipa_security.intake_owner SET scope_state=next_state,last_event_at=NEW.occurred_at
  WHERE submission_id=NEW.artifact_id::text AND request_id=NEW.request_id::text
    AND (last_event_at IS NULL OR last_event_at<=NEW.occurred_at)
    AND NOT(scope_state IN ('approved','rejected','returned') AND next_state IN ('level1','level2'))
    AND NOT(scope_state='level2' AND next_state='level1');
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS nsipa_record_security_event ON awe_req_events;
CREATE TRIGGER nsipa_record_security_event AFTER INSERT OR UPDATE ON awe_req_events FOR EACH ROW EXECUTE FUNCTION public.nsipa_security_event();

CREATE OR REPLACE FUNCTION public.nsipa_capture_document_owner() RETURNS trigger
LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
BEGIN
 IF public.nsipa_scope()='field' THEN
  NEW.created_by:=current_setting('nsipa.name',true);
  INSERT INTO nsipa_security.document_owner VALUES(NEW.document_id::text,current_setting('nsipa.sub',true)) ON CONFLICT DO NOTHING;
 END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS nsipa_document_owner ON g2p_registry_documents;
CREATE TRIGGER nsipa_document_owner BEFORE INSERT ON g2p_registry_documents FOR EACH ROW EXECUTE FUNCTION public.nsipa_capture_document_owner();

CREATE OR REPLACE FUNCTION public.nsipa_visible_document(p_id text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
 SELECT public.nsipa_scope()='admin' OR
 EXISTS(SELECT 1 FROM g2p_intake_section_documents d WHERE d.document_id::text=p_id AND public.nsipa_visible_intake(d.submission_id::text)) OR
 EXISTS(SELECT 1 FROM g2p_register_section_documents d WHERE d.document_id::text=p_id AND public.nsipa_visible_master(d.internal_record_id::text)) OR
 (NOT EXISTS(SELECT 1 FROM g2p_intake_section_documents d WHERE d.document_id::text=p_id)
 AND NOT EXISTS(SELECT 1 FROM g2p_register_section_documents d WHERE d.document_id::text=p_id)
 AND EXISTS(SELECT 1 FROM nsipa_security.document_owner o WHERE o.document_id=p_id AND o.owner_sub=current_setting('nsipa.sub',true)))
$$;

CREATE OR REPLACE FUNCTION public.nsipa_editable_document(p_id text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
 SELECT public.nsipa_scope()='field'
 AND EXISTS(SELECT 1 FROM nsipa_security.document_owner o WHERE o.document_id=p_id AND o.owner_sub=current_setting('nsipa.sub',true))
 AND NOT EXISTS(SELECT 1 FROM g2p_intake_section_documents d WHERE d.document_id::text=p_id AND NOT public.nsipa_editable_intake(d.submission_id::text))
 AND NOT EXISTS(SELECT 1 FROM g2p_register_section_documents d WHERE d.document_id::text=p_id)
$$;
