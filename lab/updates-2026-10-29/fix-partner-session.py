import json, subprocess, tempfile, pathlib

ns = ['kubectl', '-n', 'nigeria']
deploy = 'commons-services-pm-staff-portal-ui'
chunk = '[root-of-the-server]__8334ed5a._.js'
path = '/app/.next/server/chunks/' + chunk
original = subprocess.check_output(ns + ['exec', 'deploy/' + deploy, '--', 'cat', path], text=True)
old = 'n=await a.json();return m.NextResponse.json(n,{status:a.status})'
new = 'n=await a.json();if(401===a.status)return m.NextResponse.json({errors:[{code:"G2P-AUT-LOGIN-REQUIRED",message:"Authentication required"}]},{status:401});return m.NextResponse.json(n,{status:a.status})'
if original.count(old) != 1:
    raise SystemExit('Unexpected deployed version; no change made')
with tempfile.TemporaryDirectory() as tmp:
    f = pathlib.Path(tmp) / 'partner-me.js'
    f.write_text(original.replace(old, new), encoding='utf-8')
    cm = subprocess.check_output(ns + ['create', 'configmap', 'partner-session-fix-v1', '--from-file=partner-me.js=' + str(f), '--dry-run=client', '-o', 'yaml'])
    subprocess.run(ns + ['apply', '-f', '-'], input=cm, check=True)
patch = {'spec': {'template': {'spec': {'volumes': [{'name':'partner-session-fix','configMap':{'name':'partner-session-fix-v1'}}], 'containers':[{'name': 'pm-staff-portal-ui', 'volumeMounts':[{'name':'partner-session-fix','mountPath':path,'subPath':'partner-me.js','readOnly':True}]}]}}}}
deployment=json.loads(subprocess.check_output(ns+['get','deployment',deploy,'-o','json']))
patch['spec']['template']['spec']['containers'][0]['name']=deployment['spec']['template']['spec']['containers'][0]['name']
subprocess.run(ns + ['patch','deployment',deploy,'--type=strategic','-p',json.dumps(patch)],check=True)
subprocess.run(ns + ['rollout','status','deployment/'+deploy,'--timeout=120s'],check=True)
