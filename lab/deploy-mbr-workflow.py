"""Deploy the additive MBR workspace with backups; preserve all existing registry rows."""
from pathlib import Path
import datetime,json,os,py_compile,secrets,shutil,subprocess,sys
import requests,yaml

SOURCE=Path(__file__).parent
ROOT=Path('/opt/openg2p-lab/registration')
backup=ROOT/'mbr-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup.mkdir(parents=True,mode=0o700)
manifest=[]
def install(src,dest):
    dest=Path(dest);saved=backup/str(len(manifest))
    if dest.exists():shutil.copy2(dest,saved)
    manifest.append({'target':str(dest),'saved':str(saved) if saved.exists() else None})
    dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)

# Use the current runtime source; it contains independent live fixes beyond the source snapshot.
live=(ROOT/'registration_app.py').read_text()
if "'mbr':request.args.get('mbr')=='1'" not in live:
    anchor="'workspace':request.args.get('workspace')=='1',"
    assert anchor in live
    live=live.replace(anchor,"'mbr':request.args.get('mbr')=='1',"+anchor)
if " if flow.get('mbr'):" not in live:
    anchor=" if flow.get('beneficiary_profile'):"
    assert anchor in live
    live=live.replace(anchor," if flow.get('mbr'):return redirect(PREFIX+'/mbr')\n"+anchor)
if "any(role.startswith('mbr-')" not in live:
    anchor='def default_login_destination(mode,roles):'
    assert anchor in live
    live=live.replace(anchor,anchor+"\n if mode=='staff' and any(role.startswith('mbr-') for role in roles):return PREFIX+'/mbr'")
if "request.path.startswith(PREFIX+'/mbr/api/')" not in live:
    live=live.replace("request.path.startswith(PREFIX+'/api/')", "(request.path.startswith(PREFIX+'/api/') or request.path.startswith(PREFIX+'/mbr/api/'))")
if 'import mbr_workflow' not in live:
    anchor="if __name__=='__main__':"
    assert anchor in live
    live=live.replace(anchor,"import mbr_workflow\nmbr_workflow.install(os.sys.modules[__name__])\n"+anchor)
patched=backup/'registration_app.new.py';patched.write_text(live);py_compile.compile(str(patched),doraise=True)
py_compile.compile(str(SOURCE/'mbr_workflow.py'),doraise=True)

def run(*args):return subprocess.run(args,check=True,capture_output=True,text=True)
def kube(*args):return run('kubectl','-n','nigeria',*args).stdout.strip()
kc='http://'+kube('get','svc','commons-keycloak','-o','jsonpath={.spec.clusterIP}')
password=yaml.safe_load(Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password']
token=requests.post(kc+'/realms/master/protocol/openid-connect/token',data={'client_id':'admin-cli','grant_type':'password','username':'admin','password':password},timeout=20);token.raise_for_status()
s=requests.Session();s.headers['Authorization']='Bearer '+token.json()['access_token'];realm=kc+'/admin/realms/staff'
accounts=[('aarin@gmail.com','Aarin','mbr-officer'),('abuchi@gmail.com','Abuchi','mbr-field-agent'),('abutu@gmail.com','Abutu','mbr-level1'),('adaku@gmail.com','Adaku','mbr-level2'),('admin@openg2p.org','MBR Administrator','mbr-admin')]
private=ROOT/'mbr-demo-credentials.json'
credentials=json.loads(private.read_text()) if private.exists() else {}
for email,name,role in accounts:
    rr=s.get(realm+'/roles/'+role,timeout=20)
    if rr.status_code==404:s.post(realm+'/roles',json={'name':role,'description':'MBR workspace: '+role},timeout=20).raise_for_status()
    else:rr.raise_for_status()
    rr=s.get(realm+'/roles/'+role,timeout=20);rr.raise_for_status();role_data=rr.json()
    users=s.get(realm+'/users',params={'email':email,'exact':'true'},timeout=20);users.raise_for_status()
    if not users.json():
        pwd=secrets.token_urlsafe(20)
        s.post(realm+'/users',json={'username':email,'email':email,'emailVerified':True,'enabled':True,'firstName':name,'lastName':'Demo',
               'credentials':[{'type':'password','value':pwd,'temporary':False}]},timeout=20).raise_for_status()
        credentials[email]={'password':pwd,'role':role}
        private.write_text(json.dumps(credentials,indent=2));private.chmod(0o600)
        users=s.get(realm+'/users',params={'email':email,'exact':'true'},timeout=20);users.raise_for_status()
    user=users.json()[0]
    if email in credentials:
        s.put(realm+'/users/'+user['id'],json={'firstName':name,'lastName':'Demo','requiredActions':[]},timeout=20).raise_for_status()
    assigned=s.get(realm+'/users/'+user['id']+'/role-mappings/realm',timeout=20);assigned.raise_for_status()
    other=[x for x in assigned.json() if x['name'].startswith('mbr-') and x['name']!=role]
    if other:raise RuntimeError('Conflicting MBR role already assigned to '+email)
    s.post(realm+'/users/'+user['id']+'/role-mappings/realm',json=[role_data],timeout=20).raise_for_status()
try:
    install(patched,ROOT/'registration_app.py')
    install(SOURCE/'mbr_workflow.py',ROOT/'mbr_workflow.py')
    for filename in ['mbr_native_bridge.py','mbr_native_migration.py','test_mbr_db_connection.py']:
        install(SOURCE/filename,ROOT/filename)
    install(SOURCE/'registration-ui/mbr.html',ROOT/'templates/mbr.html')
    for suffix in ['js','css']:install(SOURCE/('persona-ui/dist/mbr.'+suffix),ROOT/('static/mbr.'+suffix))
    install(SOURCE/'persona-ui/dist/dashboard.js',ROOT/'static/dashboard.js')
    # Add discoverable entry points without replacing other services or deployed UI fixes.
    for path in [ROOT/'templates/base.html',ROOT/'templates/workspace.html']:
        old=path.read_text()
        if '/registration/mbr' not in old and '{{prefix}}/mbr' not in old:
            new=old.replace('<body>','<body><a style="display:block;padding:10px 24px;background:#eaf3ed;color:#146b4c;font:600 13px Segoe UI;text-decoration:none" href="/registration/mbr">Open Master Beneficiary Registry workspace ↗</a>',1)
            temp=backup/(path.stem+'.new.html');temp.write_text(new);install(temp,path)
    # Existing public home: update just the generated site bundle, keeping its HTML and other assets.
    for path in [Path('/opt/openg2p-lab/branding/site.js')]:
        if path.exists():install(SOURCE/'persona-ui/dist/site.js',path)
    (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
    run('systemctl','restart','iqs-registration')
    import time
    for attempt in range(12):
        try:
            response=requests.get('http://127.0.0.1:18081/registration/health',headers={'Host':'g2p.wverve.in'},timeout=5)
            if response.status_code==200:break
        except requests.RequestException:pass
        time.sleep(.5)
    else:raise RuntimeError('Registration service did not become healthy')
    assert requests.get('http://127.0.0.1:18081/registration/mbr',headers={'Host':'g2p.wverve.in'},allow_redirects=False,timeout=10).status_code==302
    assert requests.get('http://127.0.0.1:18081/registration/static/mbr.js',headers={'Host':'g2p.wverve.in'},timeout=10).status_code==200
    print(json.dumps({'status':'deployed','backup':str(backup),'demo_accounts':[x[0] for x in accounts],'credentials_file':str(private),'url':'https://g2p.wverve.in/registration/mbr'}))
except Exception:
    for x in reversed(manifest):
        target=Path(x['target'])
        if x['saved']:shutil.copy2(x['saved'],target)
        elif target.exists():target.unlink()
    run('systemctl','restart','iqs-registration')
    raise
