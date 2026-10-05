import subprocess, yaml, pathlib
password = yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
for service, db, command in [
    ('registry-odoo', 'socialregistrydb', ['/opt/bitnami/odoo/venv/bin/python', '/opt/bitnami/odoo/bin/odoo', 'shell', '-c', '/opt/bitnami/odoo/conf/odoo.conf']),
    ('pbms-odoo', 'pbmsdb', ['odoo', 'shell', '-c', '/etc/odoo/odoo.conf']),
]:
    script = "env.ref('base.user_admin').write(" + repr({'login': 'admin@nigeria.openg2p.localhost', 'password': password, 'name': 'Nigeria UX Administrator'}) + ")\nenv['ir.module.module'].update_list()\nenv.cr.commit()\nprint('LAB_BOOTSTRAP_COMPLETE')\n"
    result = subprocess.run(['kubectl', 'exec', '-i', '-n', 'nigeria', 'deploy/'+service, '--', *command, '-d', db, '--no-http'], input=script, text=True, capture_output=True)
    pathlib.Path('/tmp/'+service+'-bootstrap.log').write_text(result.stdout+result.stderr)
    print(service, 'exit=',result.returncode, 'completed=', 'LAB_BOOTSTRAP_COMPLETE' in result.stdout)
