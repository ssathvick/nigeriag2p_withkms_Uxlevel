"""Service-specific aggregate contracts. No record names, credentials or bank details."""
import json
from collections import Counter

SPECS = {
 'registry': {'source':'Social registry administration','database':'socialregistrydb','server':'registry-postgresql','metrics':{
  'registrant_inventory':("SELECT CASE WHEN is_group THEN 'Households' ELSE 'Individuals' END,COUNT(*) FROM res_partner WHERE is_registrant GROUP BY 1",'bars','records'),
  'registration_availability':("SELECT CASE WHEN disabled IS NOT NULL THEN 'Disabled' WHEN active THEN 'Active' ELSE 'Archived' END,COUNT(*) FROM res_partner WHERE is_registrant GROUP BY 1",'donut','registrants'),
  'household_membership_status':("SELECT COALESCE(status,'Unknown'),COUNT(*) FROM g2p_group_membership GROUP BY 1",'donut','memberships')}},
 'beneficiary': {'source':'Beneficiary portal','database':'portalpbmsdb','server':'portal-backend-postgresql','metrics':{
  'programme_availability':("SELECT CASE WHEN active THEN 'Available programmes' ELSE 'Archived programmes' END,COUNT(*) FROM g2p_program GROUP BY 1",'donut','programmes'),
  'application_membership_status':("SELECT COALESCE(state,'Unknown'),COUNT(*) FROM g2p_program_membership GROUP BY 1",'donut','memberships'),
  'memberships_by_programme':("SELECT COALESCE(p.name,'Unassigned'),COUNT(*) FROM g2p_program_membership m LEFT JOIN g2p_program p ON p.id=m.program_id GROUP BY 1 ORDER BY 2 DESC LIMIT 12",'bars','memberships')}},
 'portal-admin': {'source':'Beneficiary programme administration','database':'portalpbmsdb','server':'portal-backend-postgresql','metrics':{
  'programme_lifecycle':("SELECT COALESCE(state,'Unknown'),COUNT(*) FROM g2p_program GROUP BY 1",'donut','programmes'),
  'cycle_lifecycle':("SELECT COALESCE(state,'Unknown'),COUNT(*) FROM g2p_cycle GROUP BY 1",'donut','cycles'),
  'entitlement_lifecycle':("SELECT COALESCE(state,'Unknown'),COUNT(*) FROM g2p_entitlement GROUP BY 1",'donut','entitlements'),
  'programme_membership_status':("SELECT COALESCE(state,'Unknown'),COUNT(*) FROM g2p_program_membership GROUP BY 1",'donut','memberships')}},
 'master-data-ui': {'source':'Master data','database':'master_data','server':'commons-postgresql','metrics':{
  'geographic_reference_levels':("SELECT l.level_mnemonic,COUNT(v.level_value_id) FROM g2p_geo_levels l LEFT JOIN g2p_geo_level_values v USING(level_id) GROUP BY 1",'bars','locations'),
  'attribute_structure':("SELECT CASE WHEN is_hierarchical THEN 'Hierarchical' ELSE 'Flat' END,COUNT(*) FROM g2p_attributes GROUP BY 1",'donut','attributes'),
  'reference_inventory':("SELECT 'Attributes',COUNT(*) FROM g2p_attributes UNION ALL SELECT 'Attribute values',COUNT(*) FROM g2p_attribute_values UNION ALL SELECT 'Geographic levels',COUNT(*) FROM g2p_geo_levels",'bars','definitions'),
  'largest_attribute_catalogues':("SELECT a.attribute_display,COUNT(v.value_id) FROM g2p_attributes a LEFT JOIN g2p_attribute_values v USING(attribute_id) GROUP BY 1 ORDER BY 2 DESC LIMIT 10",'bars','values')}},
 'partner-management': {'source':'Partner management','database':'partner_management','server':'commons-postgresql','metrics':{
  'partner_status':("SELECT COALESCE(status,'Unknown'),COUNT(*) FROM pm_partners GROUP BY 1",'donut','partners'),
  'onboarding_request_status':("SELECT COALESCE(status,'Unknown'),COUNT(*) FROM pm_partner_requests GROUP BY 1",'donut','requests'),
  'request_types':("SELECT COALESCE(request_type,'Unknown'),COUNT(*) FROM pm_partner_requests GROUP BY 1",'bars','requests')}},
 'consent-manager': {'source':'Consent manager','database':'consent_manager','server':'commons-postgresql','metrics':{
  'consent_request_status':("SELECT COALESCE(status,'Unknown'),COUNT(*) FROM consent_requests GROUP BY 1",'donut','requests'),
  'consent_artefact_status':("SELECT COALESCE(status,'Unknown'),COUNT(*) FROM consent_artefacts GROUP BY 1",'donut','artefacts'),
  'consent_audit_inventory':("SELECT 'Receipts',COUNT(*) FROM consent_receipts UNION ALL SELECT 'Revocation records',COUNT(*) FROM revocation_records UNION ALL SELECT 'Consent partners',COUNT(*) FROM partners",'bars','records')}},
 'staff-portal': {'source':'Staff portal','database':'iam','server':'commons-postgresql','metrics':{
  'application_availability':("SELECT CASE WHEN active THEN 'Active applications' ELSE 'Inactive applications' END,COUNT(*) FROM staff_portal_applications GROUP BY 1",'donut','applications'),
  'roles_by_application':("SELECT a.application_mnemonic,COUNT(r.id) FROM staff_portal_applications a LEFT JOIN staff_roles r ON r.application_id=a.id GROUP BY 1 ORDER BY 2 DESC",'bars','roles'),
  'permission_catalogue_by_application':("SELECT a.application_mnemonic,COUNT(p.id) FROM staff_portal_applications a LEFT JOIN staff_application_permissions p ON p.application_id=a.id GROUP BY 1 ORDER BY 2 DESC",'bars','permission definitions')}},
 'iam-staff-ui': {'source':'Staff access administration','database':'iam','server':'commons-postgresql','restricted':True,'metrics':{
  'role_availability':("SELECT CASE WHEN active THEN 'Active roles' ELSE 'Inactive roles' END,COUNT(*) FROM staff_roles GROUP BY 1",'donut','roles'),
  'permission_availability':("SELECT CASE WHEN active THEN 'Active permissions' ELSE 'Inactive permissions' END,COUNT(*) FROM staff_application_permissions GROUP BY 1",'donut','permissions'),
  'role_permission_assignments':("SELECT CASE WHEN active THEN 'Active assignments' ELSE 'Inactive assignments' END,COUNT(*) FROM staff_role_permissions GROUP BY 1",'donut','assignments'),
  'access_configuration':("SELECT 'Data policies',COUNT(*) FROM data_policies UNION ALL SELECT 'Applications',COUNT(*) FROM staff_portal_applications",'bars','definitions')}},
 'odk': {'source':'Field data collection','database':'odkdb','server':'commons-postgresql','metrics':{
  'project_availability':('SELECT CASE WHEN archived THEN \'Archived\' ELSE \'Active\' END,COUNT(*) FROM projects WHERE "deletedAt" IS NULL GROUP BY 1','donut','projects'),
  'form_lifecycle':('SELECT COALESCE(state,\'Unknown\'),COUNT(*) FROM forms WHERE "deletedAt" IS NULL GROUP BY 1','donut','forms'),
  'submission_review_status':('SELECT COALESCE("reviewState",\'Not reviewed\'),COUNT(*) FROM submissions WHERE "deletedAt" IS NULL AND NOT draft GROUP BY 1','donut','submissions'),
  'submission_daily_volume':('SELECT "createdAt"::date::text,COUNT(*) FROM submissions WHERE "deletedAt" IS NULL AND NOT draft AND "createdAt">=CURRENT_DATE-INTERVAL \'30 days\' GROUP BY 1 ORDER BY 1','bars','submissions')}},
 'geography': {'source':'Geographic record data','database':'register','server':'commons-postgresql','restricted':True,'metrics':{
  'households_by_state':("SELECT COALESCE(state_name,'Unknown'),SUM(record_count) FROM ng2p_geography_record_counts WHERE record_type='household' GROUP BY 1 ORDER BY 2 DESC",'bars','households'),
  'individuals_by_zone':("SELECT COALESCE(zone_name,'Unknown'),SUM(record_count) FROM ng2p_geography_record_counts WHERE record_type='individual' GROUP BY 1 ORDER BY 2 DESC",'bars','individuals'),
  'household_coordinate_coverage':("SELECT 'Coordinates recorded',COALESCE(SUM(coordinates_present),0) FROM ng2p_geography_record_counts WHERE record_type='household' UNION ALL SELECT 'Coordinates missing',COALESCE(SUM(record_count-coordinates_present),0) FROM ng2p_geography_record_counts WHERE record_type='household'",'donut','households')}},
 'superset': {'source':'Analytics reporting','database':'superset','server':'commons-postgresql','metrics':{
  'dashboard_publication':("SELECT CASE WHEN published THEN 'Published' ELSE 'Draft' END,COUNT(*) FROM dashboards GROUP BY 1",'donut','dashboards'),
  'chart_types':("SELECT COALESCE(viz_type,'Unknown'),COUNT(*) FROM slices GROUP BY 1",'bars','charts'),
  'reporting_inventory':("SELECT 'Dashboards',COUNT(*) FROM dashboards UNION ALL SELECT 'Charts',COUNT(*) FROM slices UNION ALL SELECT 'Datasets',COUNT(*) FROM tables",'bars','assets')}}
}

def view_name(service,metric):return (service.replace('-','_')+'_'+metric)[:63]

def allowed(spec,roles):
 return not spec.get('restricted') or bool({'iqs-programme-supervisor','iqs-intake-reviewer'} & set(roles))

def metadata(source):
 for service,spec in SPECS.items():
  if spec['source']==source:
   return {'service_id':service,'scope':'Native synthetic sandbox records',
           'metrics':{name:{'chart':chart,'unit':unit} for name,(_,chart,unit) in spec['metrics'].items()}}
 return {}

def demos(r,service):
 records=r.rows('SELECT record_id,entity,status,region,created_at FROM dashboard_demo_records WHERE service=? ORDER BY record_id',(service,))
 groups={}
 for row in records:
  groups.setdefault(row['entity'],Counter())[row['status']]+=1
 return {'synthetic':True,'source':'Persisted demonstration dataset — separate from native operational records',
         'record_count':len(records),'data':{k:[{'label':s,'value':v} for s,v in sorted(c.items())] for k,c in groups.items()},
         'records':records}

def personal_report(r,user):
 """Caller-owned intake and linked native portal membership counts only."""
 sub=user['sub'];profile=r.one('SELECT status,sync_status,portal_partner,data FROM profiles WHERE sub=?',(sub,))
 apps=r.rows('SELECT status FROM applications WHERE sub=?',(sub,))
 data={'my_registration_status':[{'label':profile['status'],'value':1}] if profile else [],
       'my_application_status':[{'label':k,'value':v} for k,v in Counter(a['status'] for a in apps).items()]}
 errors=False
 if profile and profile.get('portal_partner'):
  try:
   import psycopg2
   cfg=json.loads((r.ROOT/'analytics-connections.json').read_text())['sources']['portalpbmsdb']
   with psycopg2.connect(**cfg,connect_timeout=5) as conn,conn.cursor() as cur:
    conn.set_session(readonly=True)
    cur.execute('SELECT status,COUNT(*) FROM nsipa_reporting.beneficiary_membership_scope WHERE partner_id=%s GROUP BY status',(profile['portal_partner'],))
    data['my_portal_memberships']=[{'label':k,'value':v} for k,v in cur.fetchall()]
  except Exception:errors=True
 now=r.stamp()
 return {'generated_at':now,'timezone':'UTC','scope':'Your own registration and application records',
  'allowed_services':['beneficiary'],'personal':True,'filters':{'state':'','programme':''},'operations':{},'knowledge':{},'snapshots':[],
  'sources':[{'source':'Beneficiary portal','service_id':'beneficiary','refreshed_at':now,'last_attempt':now,'stale':False,'error':errors,
              'scope':'Your own records only','data':data,'metrics':{k:{'chart':'donut','unit':'records'} for k in data}}], 'demo':{}}
