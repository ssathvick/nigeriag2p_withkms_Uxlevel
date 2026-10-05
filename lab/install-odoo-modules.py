import subprocess, pathlib, yaml, xmlrpc.client
password = yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
for service, db, names in [
    ('registry-odoo', 'socialregistrydb', ['g2p_social_registry', 'g2p_registry_membership', 'g2p_bank', 'g2p_registry_documents_individual', 'g2p_registry_documents_group', 'g2p_registry_id_deduplication', 'g2p_social_registry_theme', 'g2p_social_registry_dashboard', 'g2p_odk_importer']),
    ('pbms-odoo', 'pbmsdb', ['g2p_pbms', 'g2p_pbms_program_access', 'g2p_registry_addon', 'g2p_registry_type_addon', 'pbms_theme_extension', 'g2p_documents']),
]:
    ip = subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    url = f'http://{ip}'
    uid = xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate(db,'admin@nigeria.openg2p.localhost',password,{})
    if not uid:
        raise RuntimeError('Authentication failed: '+service)
    models = xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
    ids = models.execute_kw(db,uid,password,'ir.module.module','search',[[['name','in',names],['state','=','uninstalled']]])
    print(service, 'installing', len(ids), 'modules',flush=True)
    if ids:
        models.execute_kw(db,uid,password,'ir.module.module','button_immediate_install',[ids])
    print(service, 'modules installed',flush=True)
