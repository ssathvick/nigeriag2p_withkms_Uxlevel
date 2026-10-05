import subprocess,json
base='/home/openg2p/.local/lib/python3.10/site-packages/openg2p_beneficiary_portal_api/models/orm/program_orm.py'
source=subprocess.check_output(['kubectl','-n','nigeria','exec','deploy/pbms-beneficiary-portal','--','cat',base],text=True)
source=source.replace('ForeignKey("formio_builder.id")','"portal_form_builder_id", ForeignKey("formio_builder.id")') if '"portal_form_builder_id"' not in source else source
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'portal-schema-repair','namespace':'nigeria'},'data':{'program_orm.py':source}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(cm),text=True,check=True)
d=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy','pbms-beneficiary-portal','-o','json']))
s=d['spec']['template']['spec'];c=s['containers'][0]
s['volumes']=[v for v in s.get('volumes',[]) if v['name']!='portal-schema-repair']+[{'name':'portal-schema-repair','configMap':{'name':'portal-schema-repair'}}]
c['volumeMounts']=[v for v in c.get('volumeMounts',[]) if v['name']!='portal-schema-repair']+[{'name':'portal-schema-repair','mountPath':base,'subPath':'program_orm.py','readOnly':True}]
subprocess.run(['kubectl','-n','nigeria','patch','deploy','pbms-beneficiary-portal','--type=merge','-p',json.dumps({'spec':{'template':d['spec']['template']}})],check=True,stderr=subprocess.DEVNULL)
