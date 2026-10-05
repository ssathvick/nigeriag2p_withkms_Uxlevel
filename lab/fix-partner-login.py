import subprocess,json,pathlib
name='commons-services-pm-staff-portal-api'
deployment=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deployment',name,'-o','json']))
backup=pathlib.Path('/opt/openg2p-lab/partner-auth-before-fix.json')
if not backup.exists():backup.write_text(json.dumps(deployment));backup.chmod(0o600)
values={
 'PARTNER_MANAGER_AUTH_DEFAULT_ISSUERS':json.dumps(['https://keycloak.openg2p.localhost/realms/staff']),
 'PARTNER_MANAGER_AUTH_DEFAULT_JWKS_URLS':json.dumps(['http://commons-keycloak/realms/staff/protocol/openid-connect/certs']),
}
container=deployment['spec']['template']['spec']['containers'][0]
patch={'spec':{'template':{'spec':{'containers':[{'name':container['name'],'env':[{'name':k,'value':v} for k,v in values.items()]}]}}}}
subprocess.run(['kubectl','-n','nigeria','patch','deployment',name,'--type=strategic','--patch',json.dumps(patch)],check=True)
subprocess.run(['kubectl','-n','nigeria','rollout','status','deployment/'+name,'--timeout=120s'],check=True)
