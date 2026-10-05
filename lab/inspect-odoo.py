import subprocess, json, pathlib, yaml, xmlrpc.client
password = yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
for service, db in [('registry-odoo', 'socialregistrydb'), ('pbms-odoo', 'pbmsdb')]:
    ip = subprocess.check_output(['kubectl','get','svc',service,'-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
    url = f'http://{ip}'
    common = xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common')
    uid = common.authenticate(db, 'admin@nigeria.openg2p.localhost', password, {})
    print(service, 'authenticated=', bool(uid))
    if not uid:
        continue
    models = xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
    modules = models.execute_kw(db,uid,password,'ir.module.module','search_read',[[['name','ilike','g2p']]],{'fields':['name','state','shortdesc']})
    print(json.dumps(modules))
