import subprocess
script = '''import asyncio,asyncpg,os,json
async def main():
 p='MASTER_DATA_API_DB_'
 c=await asyncpg.connect(host=os.environ[p+'HOSTNAME'],port=int(os.environ[p+'PORT']),database=os.environ[p+'DBNAME'],user=os.environ[p+'USERNAME'],password=os.environ[p+'PASSWORD'])
 print([r['table_name'] for r in await c.fetch("select table_name from information_schema.tables where table_schema='public'")])
 for t in ['g2p_geo_levels','g2p_geo_level_values','g2p_sample_individuals','g2p_sample_households']:
  print(t,[dict(r) for r in await c.fetch("select column_name,data_type,is_nullable from information_schema.columns where table_name=$1",t)])
 await c.close()
asyncio.run(main())
'''
r=subprocess.run(['kubectl','exec','-i','-n','nigeria','deploy/commons-services-master-data-api','--','python','-'],input=script,text=True,capture_output=True)
print(r.stdout);print(r.stderr[-400:])
