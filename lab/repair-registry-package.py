import subprocess,json,pathlib,yaml
target='/usr/local/lib/python3.12/site-packages/openg2p_registry_core/services/g2p_register_hierarchical_service.py'
source=subprocess.check_output(['kubectl','exec','-n','nigeria','registry-inspect','--','cat',target],text=True)
line='from ..helpers.orm_cache import pair_id_key_builder, single_id_key_builder\n'
assert source.count('pair_id_key_builder')==1 and source.count('single_id_key_builder')==1, 'Imported symbols are used; patch needs review'
source=source.replace(line,'# Local packaging repair: removed unused import of a module omitted from image 1.2.1.\n')
pathlib.Path('/opt/openg2p-lab/g2p_register_hierarchical_service.py').write_text(source)
resource={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'registry-package-repair','namespace':'nigeria'},'data':{'g2p_register_hierarchical_service.py':source}}
dci_target='/usr/local/lib/python3.12/site-packages/openg2p_registry_partner_api/search/dci/services/g2p_dci_service.py'
dci_source=subprocess.check_output(['kubectl','exec','-n','nigeria','registry-partner-inspect','--','cat',dci_target],text=True)
assert dci_source.count('_engine')==1, 'DCI engine is used; patch needs review'
resource['data']['g2p_dci_service.py']=dci_source.replace('_engine = dbengine.get()', '# Local packaging repair: removed unused engine initialization with missing import.')
subprocess.run(['kubectl','apply','-f','-'],input=yaml.safe_dump(resource),text=True,check=True,stdout=subprocess.DEVNULL)
for name in ['register-partner-api','register-staff-portal-api','register-celery-worker']:
    d=json.loads(subprocess.check_output(['kubectl','get','deploy',name,'-n','nigeria','-o','json']))
    spec=d['spec']['template']['spec']; vols=spec.setdefault('volumes',[])
    if not any(v['name']=='registry-package-repair' for v in vols):vols.append({'name':'registry-package-repair','configMap':{'name':'registry-package-repair'}})
    for c in spec['containers']:
        mounts=c.setdefault('volumeMounts',[])
        if not any(m['name']=='registry-package-repair' for m in mounts):mounts.append({'name':'registry-package-repair','mountPath':target,'subPath':'g2p_register_hierarchical_service.py','readOnly':True})
        if name=='register-partner-api' and not any(m.get('subPath')=='g2p_dci_service.py' for m in mounts): mounts.append({'name':'registry-package-repair','mountPath':dci_target,'subPath':'g2p_dci_service.py','readOnly':True})
    subprocess.run(['kubectl','patch','deploy',name,'-n','nigeria','--type=merge','-p',json.dumps({'spec':{'template':{'spec':spec}}})],check=True)
print('Removed an unused import from the three affected Registry services.')
