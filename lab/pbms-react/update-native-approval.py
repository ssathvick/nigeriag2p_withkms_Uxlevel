import pathlib,json,subprocess,time,hashlib,socket
socket.setdefaulttimeout(15)
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react')
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nsipa-approval-addon','namespace':'nigeria'},'data':{p.name:p.read_text() for p in (root/'nsipa_approval').iterdir() if p.is_file()}}
def run(a,**kw):return subprocess.run(['kubectl','-n','nigeria']+a,check=True,**kw)
run(['apply','-f','-'],input=json.dumps(cm),text=True)
run(['rollout','restart','deploy/pbms-odoo'],capture_output=True)
run(['rollout','status','deploy/pbms-odoo','--timeout=180s'])
for i in range(12):
 try:
  exec((root.parent/'inspect-pbms-react.py').read_text().split('models =')[0]);break
 except Exception:
  if i==11:raise
  time.sleep(2)
code=(root/'register-native-approval.py').read_text()
exec(code[code.index("call('ir.module.module','update_list',[])"):])
