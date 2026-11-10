"""Read-only native Odoo action inventory for validated dashboard links."""
from labdb import query
import subprocess,re
bundle=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/commons-services-cm-ui','--','cat','/usr/share/nginx/html/assets/index-CcFvNVfM.js'],text=True)
print('Consent UI routes:',sorted(set(re.findall(r'path:\s*"([^"]+)"',bundle))))
for service,db in [('pbms-postgresql','pbmsdb'),('registry-postgresql','socialregistrydb'),('portal-backend-postgresql','portalpbmsdb')]:
 print(db)
 print(query(db,"SELECT a.id,a.name::text,w.res_model,w.view_mode FROM ir_act_window w JOIN ir_actions a ON a.id=w.id WHERE w.res_model LIKE 'g2p.%' OR w.res_model='res.partner' ORDER BY a.id;",host_service=service,secret_name=service))
