CREATE SCHEMA IF NOT EXISTS nsipa_security;
REVOKE ALL ON SCHEMA nsipa_security FROM PUBLIC;
CREATE TABLE IF NOT EXISTS nsipa_security.field_actors(subject text PRIMARY KEY);
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='nsipa_awe_scoped') THEN
  CREATE ROLE nsipa_awe_scoped NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
 END IF;
END $$;
GRANT USAGE ON SCHEMA public TO nsipa_awe_scoped;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO nsipa_awe_scoped;
CREATE OR REPLACE FUNCTION public.nsipa_awe_visible_request(p_id text) RETURNS boolean
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,public,nsipa_security AS $$
 SELECT EXISTS(SELECT 1 FROM public.approval_request r WHERE r.id::text=p_id AND (
 NOT r.artifact_type LIKE 'registry.%' OR current_setting('nsipa.role',true)='admin' OR (
 EXISTS(SELECT 1 FROM nsipa_security.field_actors f WHERE f.subject=r.requester)
 AND NOT EXISTS(SELECT 1 FROM approval_request newer WHERE newer.artifact_type=r.artifact_type AND newer.artifact_id=r.artifact_id AND newer.created_at>r.created_at)
 AND CASE current_setting('nsipa.role',true)
 WHEN 'level1' THEN r.status IN ('pending','in_review') AND EXISTS(SELECT 1 FROM approval_task t WHERE t.request_id=r.id AND t.stage_order=1 AND t.status IN ('open','claimed'))
 WHEN 'level2' THEN r.status IN ('pending','in_review') AND EXISTS(SELECT 1 FROM approval_task t WHERE t.request_id=r.id AND t.stage_order=2 AND t.status IN ('open','claimed'))
 WHEN 'field' THEN r.requester=current_setting('nsipa.sub',true) AND (r.status='returned' OR (r.status IN ('pending','in_review') AND EXISTS(SELECT 1 FROM approval_task t WHERE t.request_id=r.id AND t.stage_order=1 AND t.status IN ('open','claimed'))))
 WHEN 'officer' THEN r.status='approved'
 ELSE false END)))
$$;
ALTER TABLE approval_request ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS nsipa_scope_select ON approval_request;
CREATE POLICY nsipa_scope_select ON approval_request FOR SELECT TO nsipa_awe_scoped USING(nsipa_awe_visible_request(id::text));
DO $$ DECLARE t text; BEGIN
 FOREACH t IN ARRAY ARRAY['approval_task','approval_decision','approval_event'] LOOP
  EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY',t);
  EXECUTE format('DROP POLICY IF EXISTS nsipa_scope_select ON public.%I',t);
  EXECUTE format('CREATE POLICY nsipa_scope_select ON public.%I FOR SELECT TO nsipa_awe_scoped USING(nsipa_awe_visible_request(request_id::text))',t);
 END LOOP;
END $$;
ALTER TABLE webhook_delivery ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS nsipa_scope_select ON webhook_delivery;
CREATE POLICY nsipa_scope_select ON webhook_delivery FOR SELECT TO nsipa_awe_scoped USING(EXISTS(SELECT 1 FROM approval_event e WHERE e.id=webhook_delivery.event_id AND nsipa_awe_visible_request(e.request_id::text)));
