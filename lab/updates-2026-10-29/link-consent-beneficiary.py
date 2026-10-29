"""Route the staff UI's personal-consent link to beneficiary sign-in."""
import json, pathlib, subprocess, tempfile
ns=['kubectl','-n','nigeria']; dep='commons-services-cm-ui'
filename='index-CcFvNVfM.js'; path='/usr/share/nginx/html/assets/'+filename
original=subprocess.check_output(ns+['exec','deploy/'+dep,'--','cat',path],text=True)
old='u.jsx(ks,{to:"/my/consents",className:Cs,children:"My Consents"})'
new='u.jsx("a",{href:"https://beneficiary-consent.nigeriag2p.com/my/consents",children:"My Consents"})'
if original.count(old)!=1: raise SystemExit('Unexpected UI version: no changes made')
with tempfile.TemporaryDirectory() as d:
 f=pathlib.Path(d)/filename; f.write_text(original.replace(old,new),encoding='utf-8')
 cm=subprocess.check_output(ns+['create','configmap','nigeria-consent-staff-link-v1','--from-file='+str(f),'--dry-run=client','-o','yaml'])
 subprocess.run(ns+['apply','--server-side','-f','-'],input=cm,check=True)
deployment=json.loads(subprocess.check_output(ns+['get','deployment',dep,'-o','json']))
name=deployment['spec']['template']['spec']['containers'][0]['name']
patch={'spec':{'template':{'spec':{'volumes':[{'name':'beneficiary-consent-link','configMap':{'name':'nigeria-consent-staff-link-v1'}}],'containers':[{'name':name,'volumeMounts':[{'name':'beneficiary-consent-link','mountPath':path,'subPath':filename,'readOnly':True}]}]}}}}
subprocess.run(ns+['patch','deployment',dep,'--type=strategic','-p',json.dumps(patch)],check=True)
subprocess.run(ns+['rollout','status','deployment/'+dep,'--timeout=120s'],check=True)
