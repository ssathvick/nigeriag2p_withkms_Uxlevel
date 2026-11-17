"""Fixed aggregate-only geography boundary for the read-only reporting identity.

The native record geography view retains security_invoker for scoped application reads.
This no-argument function exposes only pre-aggregated counts to the existing reporting
role; it grants no access to household/individual rows or application mutations.
"""
GEOGRAPHY_AGGREGATES_SQL = '''
CREATE OR REPLACE FUNCTION nsipa_reporting.geography_record_counts()
RETURNS TABLE(record_type text, zone_name text, state_name text,
              record_count bigint, coordinates_present bigint)
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = pg_catalog
AS $geography_counts$
    SELECT record_type::text, zone_name::text, state_name::text,
           record_count::bigint, coordinates_present::bigint
    FROM public.ng2p_geography_record_counts
$geography_counts$;
REVOKE ALL ON FUNCTION nsipa_reporting.geography_record_counts() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION nsipa_reporting.geography_record_counts() TO g2p_analytics_reader;
COMMENT ON FUNCTION nsipa_reporting.geography_record_counts() IS
'Fixed read-only state/zone registry aggregates; no identifiers, coordinates or input parameters. Native invoker view and RLS remain unchanged.';
'''

def provision_geography_aggregates(cursor):
    cursor.execute(GEOGRAPHY_AGGREGATES_SQL)
