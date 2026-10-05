import subprocess,json,pathlib
states=['Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue','Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi','Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo','Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara','Federal Capital Territory']
levels=[{'level_id':'country','level_mnemonic':'Country','parent_level_id':None},{'level_id':'state','level_mnemonic':'State / FCT','parent_level_id':'country'},{'level_id':'lga','level_mnemonic':'Local Government Area','parent_level_id':'state'}]
values=[{'level_value_id':'NG','level_id':'country','level_value_mnemonic':'Nigeria','parent_level_value_id':None}]
codes={name:'NG'+str(i+1).zfill(2) for i,name in enumerate(states)}
values += [{'level_value_id':codes[name],'level_id':'state','level_value_mnemonic':name,'parent_level_value_id':'NG'} for name in states]
for state,lga in [('Kano','Dala'),('Kano','Nassarawa'),('Lagos','Ikeja'),('Lagos','Surulere'),('Kaduna','Chikun'),('Federal Capital Territory','Abuja Municipal')]:
    n=1+sum(v['parent_level_value_id']==codes[state] for v in values if v['level_id']=='lga')
    values.append({'level_value_id':codes[state]+str(n).zfill(2),'level_id':'lga','level_value_mnemonic':lga,'parent_level_value_id':codes[state]})
people=[]
for i,(first,last) in enumerate([('Fatima','Abubakar'),('Musa','Ibrahim'),('Amina','Bello'),('Chinedu','Okafor'),('Ngozi','Nwosu'),('Babatunde','Adeyemi'),('Aisha','Suleiman'),('Grace','Eze'),('Yusuf','Ali'),('Maryam','Usman'),('Emeka','Obi'),('Funmi','Adebayo')]):
    people.append({'individual_id':f'NG-LAB-{i+1:04d}','given_name':first,'fathers_name':last,'full_name':first+' '+last,'gender':'FEMALE' if i%2==0 else 'MALE','household_id':f'NG-LAB-HH-{i//2+1:03d}','national_id':f'NG-LAB-ID-{i+1:04d}','country':'NGA','geo_pcode':codes['Kano']+'01' if i<6 else codes['Lagos']+'01','birth_year':1980+i,'version':'nigeria-ux-lab-1'})
fixture={'manifest':{'country':'NGA','synthetic':True,'note':'UX lab fixtures. People and identifiers are invented. Geographic codes are local lab identifiers, not official Nigerian P-codes. LGA coverage is a demonstration subset; no boundary geometry supplied.'},'levels':levels,'values':values,'people':people}
pathlib.Path('/opt/openg2p-lab/nigeria-fixtures.json').write_text(json.dumps(fixture,indent=2))
pathlib.Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/nigeria-fixtures.json').write_text(json.dumps(fixture,indent=2))
script='fixture='+repr(fixture)+'''\nimport asyncio,asyncpg,os
async def main():
 p='MASTER_DATA_API_DB_'
 c=await asyncpg.connect(host=os.environ[p+'HOSTNAME'],port=int(os.environ[p+'PORT']),database=os.environ[p+'DBNAME'],user=os.environ[p+'USERNAME'],password=os.environ[p+'PASSWORD'])
 async with c.transaction():
  # This environment was created for this task; replace only upstream demo geography and sample-person fixtures.
  await c.execute('TRUNCATE g2p_geo_level_values, g2p_geo_levels, g2p_sample_individuals, g2p_sample_households CASCADE')
  for r in fixture['levels']:await c.execute('INSERT INTO g2p_geo_levels(level_id,level_mnemonic,parent_level_id) VALUES($1,$2,$3)',r['level_id'],r['level_mnemonic'],r['parent_level_id'])
  for r in fixture['values']:await c.execute('INSERT INTO g2p_geo_level_values(level_value_id,level_id,level_value_mnemonic,parent_level_value_id) VALUES($1,$2,$3,$4)',r['level_value_id'],r['level_id'],r['level_value_mnemonic'],r['parent_level_value_id'])
  for r in fixture['people']:await c.execute('INSERT INTO g2p_sample_individuals(individual_id,given_name,fathers_name,full_name,gender,household_id,national_id,country,geo_pcode,birth_year,version) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)',*[r[k] for k in ['individual_id','given_name','fathers_name','full_name','gender','household_id','national_id','country','geo_pcode','birth_year','version']])
  for i in range(6):
   head=fixture['people'][i*2]
   await c.execute('INSERT INTO g2p_sample_households(household_id,head_individual_id,size_total,country,geo_pcode,version) VALUES($1,$2,$3,$4,$5,$6)',head['household_id'],head['individual_id'],2,'NGA',head['geo_pcode'],'nigeria-ux-lab-1')
 print('Nigeria master data seeded: 37 states/FCT, 6 sample LGAs, 12 synthetic people, 6 synthetic households.')
 await c.close()
asyncio.run(main())
'''
r=subprocess.run(['kubectl','exec','-i','-n','nigeria','deploy/commons-services-master-data-api','--','python','-'],input=script,text=True,capture_output=True)
print(r.stdout);print(r.stderr[-500:]);r.check_returncode()
