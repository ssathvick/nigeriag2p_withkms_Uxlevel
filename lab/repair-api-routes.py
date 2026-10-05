import subprocess,json
for name,service in [('bridge-api','bridge-api'),('spar-openg2p-spar-mapper-api','spar-openg2p-spar-mapper-api')]:
 obj=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','vs',name,'-o','json']))
 route={'match':[{'uri':{'prefix':'/'}}],'route':[{'destination':{'host':service,'port':{'number':80}}}]}
 obj['spec']['http']=[r for r in obj['spec']['http'] if r.get('match',[{}])[0].get('uri',{}).get('prefix')!='/']+[route]
 if name=='bridge-api':
  for r in obj['spec']['http']:
   for destination in r['route']:destination['destination']['host']=service
 subprocess.run(['kubectl','-n','nigeria','patch','vs',name,'--type=merge','-p',json.dumps({'spec':obj['spec']})],check=True)
