import subprocess,json
from pathlib import Path
root=Path(__file__).parent/'meeting-native';root.mkdir(exist_ok=True)
groups={
 'register-staff-portal-api':('/usr/local/lib/python3.12/site-packages/',[
 'openg2p_registry_core/schemas/change_request.py','openg2p_registry_core/schemas/intake_form.py','openg2p_registry_core/services/intake_form_data_service.py','openg2p_registry_core/services/g2p_awe_webhook_service.py','openg2p_registry_core/helpers/awe_helper.py','openg2p_registry_core/controller_services/g2p_awe_proxy_controller_service.py','openg2p_registry_core/services/g2p_awe_integration_service.py','openg2p_registry_core/services/g2p_register_change_request_service.py','openg2p_registry_core/services/g2p_awe_status_reconcile.py','openg2p_registry_core/helpers/awe_status_summary.py',
 'openg2p_registry_extensions/register_domain/models/household.py','openg2p_registry_extensions/register_domain/schemas/household.py','openg2p_registry_extensions/register_domain/models/individual.py','openg2p_registry_extensions/register_domain/schemas/individual.py']),
 'commons-services-awe':('/usr/local/lib/python3.13/site-packages/',['awe/services/engine.py','awe/controllers/task.py','awe/schemas/request.py','awe/services/webhook.py','awe/schemas/callback.py'])}
manifest={}
for deployment,(base,files) in groups.items():
 manifest[deployment]={}
 for file in files:
  p=root/'original'/deployment/file;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():
   try:p.write_text(subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/'+deployment,'--','cat',base+file],text=True,stderr=subprocess.DEVNULL))
   except subprocess.CalledProcessError:continue
  manifest[deployment][str(p.relative_to(root))]=base+file
(root/'manifest.json').write_text(json.dumps(manifest,indent=2));print({k:len(v) for k,v in manifest.items()})
for file in ['models/household.py','schemas/household.py','models/individual.py','schemas/individual.py']:
 path='/app/reference-extension/src/openg2p_registry_reference_extension/register_domain/'+file
 p=root/'original/register-staff-portal-api/reference'/file;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():p.write_text(subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/register-staff-portal-api','--','cat',path],text=True,stderr=subprocess.DEVNULL))
 manifest['register-staff-portal-api'][str(p.relative_to(root))]='/usr/local/lib/python3.12/site-packages/openg2p_registry_reference_extension/register_domain/'+file
(root/'manifest.json').write_text(json.dumps(manifest,indent=2))
