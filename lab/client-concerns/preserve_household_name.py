from pathlib import Path
from overlay import deploy
root=Path(__file__).parent;name='g2p_register_domain_service_household.py'
s=(root/'runtime'/name).read_text()
for message in ['Constructing intake record name for household','Constructing record name for household']:
 old=f'_logger.info("{message}")'
 s=s.replace(old,old+'\n        supplied_name = str(payload.get("record_name") or "").strip()\n        if supplied_name:\n            return supplied_name')
(root/'patched'/name).write_text(s)
for app in ['register-staff-portal-api','register-celery-worker']:
 deploy(app,'nsipa-household-name',{'/usr/local/lib/python3.12/site-packages/openg2p_registry_reference_extension/register_domain/services/'+name:s})

