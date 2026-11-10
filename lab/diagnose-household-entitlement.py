import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
pb=r.Odoo('pbms-odoo','pbmsdb')
print('Rules',pb.call('g2p.entitlement.rule.definition','search_read',[[['program_id','=',39]]],{'fields':['pbms_domain','sql_query','quantity','multiplier','decimal_places']}))
with r.pg('bgtaskdb','pbms-postgresql') as c:
 with c.cursor() as cur:
  cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%beneficiary%'");print('Tables',cur.fetchall())
  cur.execute('SELECT beneficiary_list_id FROM g2p_beneficiary_list WHERE id=6') if False else None
listing=pb.call('g2p.beneficiary.list','read',[[6]],{'fields':['beneficiary_list_id','number_of_entitlements_processed','number_of_registrants','entitlement_process_status']})[0];print('List',listing)
with r.pg('bgtaskdb','pbms-postgresql') as c:
 with c.cursor() as cur:
  cur.execute('SELECT id,registrant_details,entitlement_process_status FROM beneficiary_list_details WHERE beneficiary_list_id=%s',(listing['beneficiary_list_id'],));print('Details',cur.fetchall())
