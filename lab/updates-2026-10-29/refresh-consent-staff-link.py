import json,subprocess,tempfile,pathlib
ns=['kubectl','-n','nigeria'];dep='commons-services-cm-ui'
p='/usr/share/nginx/html/index.html';s=subprocess.check_output(ns+['exec','deploy/'+dep,'--','cat',p],text=True)
old='/assets/index-CcFvNVfM.js'; assert s.count(old)==1
with tempfile.TemporaryDirectory() as d:
 f=pathlib.Path(d)/'index.html';f.write_text(s.replace(old,old+'?beneficiary-link=1'),encoding='utf-8')
 cm=subprocess.check_output(ns+['create','configmap','nigeria-consent-staff-index-v1','--from-file='+str(f),'--dry-run=client','-o','yaml'])
 subprocess.run(ns+['apply','--server-side','-f','-'],input=cm,check=True)
deployment=json.loads(subprocess.check_output(ns+['get','deployment',dep,'-o','json']))
n=deployment['spec']['template']['spec']['containers'][0]['name']
patch={'spec':{'template':{'spec':{'volumes':[{'name':'beneficiary-consent-index','configMap':{'name':'nigeria-consent-staff-index-v1'}}],'containers':[{'name':n,'volumeMounts':[{'name':'beneficiary-consent-index','mountPath':p,'subPath':'index.html','readOnly':True}]}]}}}}
subprocess.run(ns+['patch','deployment',dep,'--type=strategic','-p',json.dumps(patch)],check=True)
subprocess.run(ns+['rollout','status','deployment/'+dep,'--timeout=120s'],check=True)
