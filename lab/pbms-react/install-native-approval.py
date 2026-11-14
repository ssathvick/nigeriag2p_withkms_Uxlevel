"""Install persistent NSIPA native PBMS extension with backup and declared pod mount."""
import datetime,json,pathlib,subprocess,tarfile,io,time,socket
socket.setdefaulttimeout(15)
root=pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/pbms-react')
def cmd(args,**kw):return subprocess.run(args,check=True,**kw)
def k(args,**kw):return cmd(['kubectl','-n','nigeria']+args,**kw)
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup=pathlib.Path('/opt/openg2p-lab/pbms-react/backups/native-'+stamp);backup.mkdir(mode=0o700)
dep=json.loads(subprocess.check_output(['kubectl','-n','nigeria','get','deploy','pbms-odoo','-o','json']))
(backup/'deployment.json').write_text(json.dumps(dep))
# Database and filestore remain on the existing persistent volume.
with (backup/'pbmsdb.sql').open('wb') as out:
 k(['exec','pbms-postgresql-0','--','sh','-c','PGPASSWORD="$POSTGRES_POSTGRES_PASSWORD" pg_dump -U postgres pbmsdb'],stdout=out)
(backup/'pbmsdb.sql').chmod(0o600)
cm={'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':'nsipa-approval-addon','namespace':'nigeria'},'data':{p.name:p.read_text() for p in (root/'nsipa_approval').iterdir() if p.is_file()}}
k(['apply','-f','-'],input=json.dumps(cm),text=True)
spec=dep['spec']['template']['spec'];vols=spec['volumes'];mounts=spec['containers'][0]['volumeMounts']
vols[:]=[v for v in vols if v['name']!='nsipa-approval-addon'];mounts[:]=[v for v in mounts if v['name']!='nsipa-approval-addon']
vols.append({'name':'nsipa-approval-addon','configMap':{'name':'nsipa-approval-addon'}})
mounts.append({'name':'nsipa-approval-addon','mountPath':'/opt/odoo/extraaddons/openg2p-pbms/nsipa_approval','readOnly':True})
k(['patch','deploy','pbms-odoo','--type=merge','-p',json.dumps({'spec':{'template':{'metadata':{'annotations':{'nsipa-release':stamp}},'spec':{'volumes':vols,'containers':spec['containers']}}}})],stdout=subprocess.DEVNULL)
k(['rollout','status','deploy/pbms-odoo','--timeout=180s'])
for attempt in range(12):
    try:
        exec((root.parent/'inspect-pbms-react.py').read_text().split('models =')[0]);break
    except (OSError,ConnectionError):
        if attempt==11:raise
        time.sleep(2)
call('ir.module.module','update_list',[])
module=call('ir.module.module','search',[[['name','=','nsipa_approval']]])
state=call('ir.module.module','read',[module],{'fields':['state']})[0]['state']
call('ir.module.module','button_immediate_upgrade' if state=='installed' else 'button_immediate_install',[module])
print('Native approval module installed. Backup:',backup)
