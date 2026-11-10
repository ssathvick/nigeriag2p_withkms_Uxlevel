"""Read-only frontend inventory; never prints credentials or beneficiary records."""
import json, pathlib, subprocess, xmlrpc.client, yaml
password = yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
ip = subprocess.check_output(['kubectl','get','svc','pbms-odoo','-n','nigeria','-o','jsonpath={.spec.clusterIP}'], text=True).strip()
uid = xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/common').authenticate('pbmsdb','admin@nigeria.openg2p.localhost',password,{})
proxy = xmlrpc.client.ServerProxy('http://'+ip+'/xmlrpc/2/object')
def call(model, method, args, kw=None):
    return proxy.execute_kw('pbmsdb', uid, password, model, method, args, kw or {})
models = call('ir.model', 'search_read', [[['model','like','g2p.%']]], {'fields':['model','name']})
views = call('ir.ui.view','search_read',[[['model','like','g2p.%'],['type','in',['form','tree']]]],{'fields':['model','type','arch_db','inherit_id']})
actions = call('ir.actions.act_window','search_read',[[['res_model','like','g2p.%']]],{'fields':['name','res_model','domain','context']})
out = {'models':models,'views':views,'actions':actions}
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-inventory.json').write_text(json.dumps(out, indent=2))
print(json.dumps({'models':models,'actions':actions},indent=2))
