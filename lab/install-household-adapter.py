"""IQS sandbox household adapter; retain original farmer/student adapters."""
import subprocess,json,pathlib,sys,xmlrpc.client,yaml,time,hashlib
ROOT=pathlib.Path('/opt/openg2p-lab/household-adapter');ROOT.mkdir(exist_ok=True)
def run(*a):return subprocess.check_output(a,text=True,stderr=subprocess.DEVNULL)
def read(deploy,path):return run('kubectl','-n','nigeria','exec','deploy/'+deploy,'--','cat',path)
def apply(obj):subprocess.run(['kubectl','apply','-f','-'],input=json.dumps(obj),text=True,check=True,stdout=subprocess.DEVNULL)
def mount(deploy,name,files):
 data={f'f{i}':text for i,(path,text) in enumerate(files.items())}
 apply({'apiVersion':'v1','kind':'ConfigMap','metadata':{'name':name,'namespace':'nigeria'},'data':data})
 d=json.loads(run('kubectl','-n','nigeria','get','deploy',deploy,'-o','json'));s=d['spec']['template']['spec'];c=s['containers'][0]
 d['spec']['template'].setdefault('metadata',{}).setdefault('annotations',{})[name+'-hash']=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
 s['volumes']=[v for v in s.get('volumes',[]) if v['name']!=name]+[{'name':name,'configMap':{'name':name}}]
 c['volumeMounts']=[v for v in c.get('volumeMounts',[]) if v['name']!=name]+[{'name':name,'mountPath':p,'subPath':f'f{i}','readOnly':True} for i,p in enumerate(files)]
 apply(d)
 for p,t in files.items():
  dest=ROOT/deploy/p.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(t)
def trans(t):
 for a,b in [('Farmer','Household'),('farmer','household'),('FARMER','HOUSEHOLD'),('land_area','size_total'),('land_holding','household_size'),('no_of_cattle_heads','size_adults'),('no_of_poultry_heads','size_children'),('acres','members'),('INR','NGN')]:t=t.replace(a,b)
 return t
odbase='/opt/odoo/extraaddons/openg2p-pbms-extensions/'
typepath=odbase+'g2p_registry_type_addon/models/registry_type.py'
types=read('pbms-odoo',typepath)
if 'HOUSEHOLD' not in types:types=types.replace('OTHER = "other"','HOUSEHOLD = "household"\n    OTHER = "other"').replace('"student": "g2p.student.registry",','"household": "g2p.household.registry",\n        "student": "g2p.student.registry",')
addon=odbase+'iqs_household_registry/'
model='''from odoo import models,fields
class Household(models.Model):
    _name='g2p.household.registry'
    _description='IQS Household Registry'
    _inherit='g2p.registry'
    name=fields.Char(required=True)
    gender=fields.Selection([('male','Male head'),('female','Female head'),('other','Other')])
    size_total=fields.Integer(string='Household members')
    size_adults=fields.Integer(string='Adults')
    size_children=fields.Integer(string='Children')
    annual_income=fields.Float(string='Annual household income (NGN)')
    large_area_id=fields.Integer()
    large_area_code=fields.Char(string='State / FCT')
    small_area_id=fields.Integer()
    small_area_code=fields.Char(string='Community')
    _sql_constraints=[('link_unique','unique(link_registry_id)','A household reference must be unique.')]
class ApplicationScope(models.Model):
    _inherit='g2p.beneficiary.list'
    iqs_household_ref=fields.Char(string='IQS application household reference',readonly=True)
'''
view=trans(read('pbms-odoo',odbase+'g2p_registry_addon/views/registry/farmer_registry_view.xml')).replace('create="0"','')
view=view.replace('</odoo>','<menuitem id="menu_iqs_households" name="Household Registry" parent="g2p_pbms.menu_g2p_registry" action="action_g2p_household_registry" sequence="3"/></odoo>')
files={typepath:types,addon+'__init__.py':'from . import models\n',addon+'__manifest__.py':repr({'name':'IQS Household Registry Adapter','version':'3.0.0','license':'LGPL-3','depends':['g2p_registry_addon'],'data':['security/ir.model.access.csv','views/household.xml'],'installable':True}),addon+'models/__init__.py':'from . import household\n',addon+'models/household.py':model,addon+'security/ir.model.access.csv':'id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\naccess_iqs_household,IQS household,model_g2p_household_registry,base.group_user,1,1,1,0\n',addon+'views/household.xml':view}
mount('pbms-odoo','iqs-household-odoo',files)
subprocess.run(['kubectl','-n','nigeria','rollout','status','deploy/pbms-odoo','--timeout=180s'],check=True)
pwd=yaml.safe_load(pathlib.Path('/opt/openg2p-lab/credentials.yaml').read_text())['admin_password'];ip=run('kubectl','-n','nigeria','get','svc','pbms-odoo','-o','jsonpath={.spec.clusterIP}').strip();url='http://'+ip
for attempt in range(30):
 try:
  uid=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/common').authenticate('pbmsdb','admin@nigeria.openg2p.localhost',pwd,{});break
 except ConnectionError:time.sleep(2)
m=xmlrpc.client.ServerProxy(url+'/xmlrpc/2/object')
def call(model,method,args,kw={}):return m.execute_kw('pbmsdb',uid,pwd,model,method,args,kw)
call('ir.module.module','update_list',[]);ids=call('ir.module.module','search',[[['name','=','iqs_household_registry'],['state','=','uninstalled']]])
if ids:call('ir.module.module','button_immediate_install',[ids])
else:
 ids=call('ir.module.module','search',[[['name','=','iqs_household_registry']]])
 call('ir.module.module','button_immediate_upgrade',[ids])
base='/usr/local/lib/python3.12/site-packages/openg2p_bg_task_registry_adapters/'
files={}
for part,names in {'models':['registry_farmer.py','beneficiary_list_summary_farmer.py'],'schema':['registry_farmer.py','beneficiary_list_summary_farmer.py'],'computations':['registry_farmer.py']}.items():
 for name in names:files[base+part+'/'+name.replace('farmer','household')]=trans(read('pbms-celery-worker',base+part+'/'+name))
 for partfile in ['__init__.py']:
  t=read('pbms-celery-worker',base+part+'/'+partfile)
  extra='\n'+ '\n'.join(trans(line) for line in t.splitlines() if 'registry_farmer import' in line or 'beneficiary_list_summary_farmer import' in line)
  # Multiline schema exports need complete import blocks.
  if part=='schema':extra='\nfrom .registry_household import G2PHouseholdRegistryPayload\nfrom .beneficiary_list_summary_household import BeneficiaryListSummaryHousehold,BeneficiaryListSummaryHouseholdPayload\n'
  if 'registry_household import' not in t:t+=extra
  files[base+part+'/'+partfile]=t
t=read('pbms-celery-worker',base+'models/registry_type.py')
if 'HOUSEHOLD' not in t:t=t.replace('OTHER = "other"','HOUSEHOLD = "household"\n    OTHER = "other"')
files[base+'models/registry_type.py']=t
t=read('pbms-celery-worker',base+'factory/registry_factory.py')
if 'return RegistryHousehold()' not in t:t=t.replace('class RegistryFactory:', 'from ..computations.registry_household import RegistryHousehold\n\nclass RegistryFactory:').replace('if target_registry == G2PRegistryType.FARMER.value:', 'if target_registry == "household":\n            return RegistryHousehold()\n\n        if target_registry == G2PRegistryType.FARMER.value:')
files[base+'factory/registry_factory.py']=t
taskpath='/usr/local/lib/python3.12/site-packages/openg2p_bg_task_celery_workers/tasks/beneficiary_list_worker.py'
t=read('pbms-celery-worker',taskpath)
if '# IQS per-application household scope' not in t:
 marker='            registry_cursor = sr_session.execute(constructed_query)'
 scope='''            # IQS per-application household scope: a list must never enroll another applicant.
            if g2p_program_definition.target_registry == 'household' and beneficiary_list.mnemonic.startswith('IQS-REG-APP-'):
                from sqlalchemy import text as iqs_text
                iqs_ref = pbms_session.execute(iqs_text('SELECT iqs_household_ref FROM g2p_beneficiary_list WHERE id=:id'), {'id': id}).scalar_one()
                if not iqs_ref:
                    raise ValueError('IQS application household scope is missing')
                constructed_query = iqs_text('SELECT link_registry_id FROM (' + str(constructed_query).rstrip(';') + ') AS iqs_candidate WHERE link_registry_id=:iqs_household').bindparams(iqs_household=iqs_ref)
'''
 if marker not in t:raise RuntimeError('Unsupported worker source; scope marker not found')
 t=t.replace(marker,scope+marker)
files[taskpath]=t
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
# The summary table uses the same base schema and dedicated household statistics.
sql='CREATE TABLE IF NOT EXISTS beneficiary_list_summary_household (LIKE beneficiary_list_summary_farmer INCLUDING DEFAULTS INCLUDING CONSTRAINTS INCLUDING INDEXES);'
for suffix in ['q1','q2','q3','mean','units']:
 sql+=f"DO $$ BEGIN IF EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='beneficiary_list_summary_household' AND column_name='land_holding_{suffix}') THEN ALTER TABLE beneficiary_list_summary_household RENAME COLUMN land_holding_{suffix} TO household_size_{suffix}; END IF; END $$;"
query('bgtaskdb',sql,host_service='pbms-postgresql',secret_name='pbms-postgresql')
for deploy in ['pbms-celery-worker','pbms-celery-beat-producer','pbms-api']:mount(deploy,'iqs-household-worker',files)
print('Household adapter installed in Odoo, API and background workers.')
