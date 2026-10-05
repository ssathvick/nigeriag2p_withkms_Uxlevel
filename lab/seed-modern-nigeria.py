import json,sys,subprocess,uuid
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
from labdb import query
fixture=json.load(open('/opt/openg2p-lab/nigeria-fixtures.json'))
def q(s):return "'"+str(s).replace("'","''")+"'"
sql=[]
for i,p in enumerate(fixture['people']):
 rid=str(uuid.uuid5(uuid.NAMESPACE_URL,'openg2p-lab/'+p['individual_id']))
 hid=str(uuid.uuid5(uuid.NAMESPACE_URL,'openg2p-lab/'+p['household_id']))
 national=f'900000{i+1:06d}'
 sql.append(f"UPDATE g2p_sample_individuals SET birth_date='{p['birth_year']}-01-15', national_id={q(national)} WHERE individual_id={q(p['individual_id'])};")
 p['national_id']=national;p['birth_date']=f"{p['birth_year']}-01-15"
 fields=['internal_record_id','functional_record_id','link_internal_record_id','record_name','created_by','created_at','last_approved_at','last_approved_by','record_status','search_text','foundational_id','first_name','last_name','given_name','full_name','gender','birth_date','country_code','geo_lowest_level_value_id']
 vals=[rid,p['individual_id'],hid,p['full_name'],'nigeria-lab','2026-10-03','2026-10-03','nigeria-lab','ACTIVE',p['full_name'],national,p['given_name'],p['fathers_name'],p['given_name'],p['full_name'],p['gender'],p['birth_date'],'NGA',p['geo_pcode']]
 statement=f"INSERT INTO g2p_register_individuals({','.join(fields)}) VALUES({','.join(q(v) for v in vals)}) ON CONFLICT(internal_record_id) DO NOTHING;"
 query('register',statement)
 if i%2==0:
  fields=['internal_record_id','functional_record_id','record_name','created_by','created_at','last_approved_at','last_approved_by','record_status','search_text','household_head_internal_record_id','household_head_name','size_total','size_adults','country_code','geo_lowest_level_value_id']
  vals=[hid,p['household_id'],p['full_name']+' household','nigeria-lab','2026-10-03','2026-10-03','nigeria-lab','ACTIVE',p['full_name']+' household',rid,p['full_name'],2,2,'NGA',p['geo_pcode']]
  query('register',f"INSERT INTO g2p_register_households({','.join(fields)}) VALUES({','.join(q(v) for v in vals)}) ON CONFLICT(internal_record_id) DO NOTHING;")
query('master_data','\n'.join(sql))
for path in ['/opt/openg2p-lab/nigeria-fixtures.json','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/nigeria-fixtures.json']:
 json.dump(fixture,open(path,'w'),indent=2)
subprocess.run(['kubectl','delete','job','nigeria-identity-seed','nigeria-register-seed','-n','nigeria','--ignore-not-found'],check=True)
job=json.loads(subprocess.check_output(['kubectl','get','job','commons-services-mock-identity-system-identity-seed','-n','nigeria','-o','json']))
spec=job['spec'];spec.pop('selector',None);spec.pop('manualSelector',None);spec['template']['metadata']={'labels':{'app':'nigeria-identity-seed'}}
subprocess.run(['kubectl','apply','-f','-'],input=json.dumps({'apiVersion':'batch/v1','kind':'Job','metadata':{'name':'nigeria-identity-seed','namespace':'nigeria'},'spec':spec}),text=True,check=True)
print('Modern registry seeded with 12 synthetic people and 6 households. Mock identity seed restarted.')
