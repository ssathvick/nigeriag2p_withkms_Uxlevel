"""Restore missing existing PBMS connection settings; no backend code changes."""
import json,pathlib,datetime
exec(pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/inspect-pbms-react.py').read_text().split('models =')[0])
settings={'g2p_pbms.staff_portal_api_url':'http://pbms-api','g2p_pbms.g2p_bridge_api_url':'http://bridge-api','g2p_pbms.keymanager_toggle':'True','g2p_pbms.keymanager_api_base_url':'http://commons-services-keymanager/v1/keymanager','g2p_pbms.keymanager_sign_application_id':'OPENG2P_PBMS'}
previous={key:call('ir.config_parameter','get_param',[key]) for key in settings}
path=pathlib.Path('/opt/openg2p-lab/pbms-react/backups')/('workflow-settings-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')
path.write_text(json.dumps(previous));path.chmod(0o600)
for key,value in settings.items():
    if not previous[key]:call('ir.config_parameter','set_param',[key,value])
    print(key,call('ir.config_parameter','get_param',[key]))
print('Prior settings saved privately:',str(path))
