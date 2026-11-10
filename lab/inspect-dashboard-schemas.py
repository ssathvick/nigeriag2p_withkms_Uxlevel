"""Read-only schema inventory. Never print credentials or record contents."""
from labdb import query
databases={'commons-postgresql':['partner_management','consent_manager','iam','master_data','odkdb','superset'], 'registry-postgresql':['socialregistrydb'],'portal-backend-postgresql':['portalpbmsdb']}
for service,dbs in databases.items():
 for db in dbs:
  rows=query(db,"SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;",host_service=service,secret_name=service).splitlines()
  if db in ['socialregistrydb','portalpbmsdb']:rows=[t for t in rows if t.startswith('g2p_') or t in ['res_partner','res_users']]
  chosen={'partner_management':['pm_partners','pm_partner_requests'], 'consent_manager':['consent_requests','consent_artefacts','consent_receipts','partners','revocation_records'], 'iam':['staff_portal_applications','staff_roles','staff_application_permissions','staff_role_permissions','data_policies'], 'master_data':['g2p_geo_levels','g2p_geo_level_values','g2p_attributes','g2p_attribute_values'], 'odkdb':['projects','forms','submissions','entities'], 'superset':['dashboards','slices','tables'], 'socialregistrydb':['res_partner','g2p_group_membership','g2p_reg_id'],'portalpbmsdb':['g2p_program','g2p_program_membership','g2p_cycle','g2p_entitlement','g2p_payment','res_partner']}[db]
  for table in chosen:
   print(db,table,'count='+query(db,'SELECT count(*) FROM "'+table+'";',host_service=service,secret_name=service).strip())
   print(query(db,"SELECT column_name||':'||data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='"+table+"' ORDER BY ordinal_position;",host_service=service,secret_name=service).strip())
