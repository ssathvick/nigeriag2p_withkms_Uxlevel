import subprocess
script='''import asyncio
from openg2p_g2p_bridge_celery_workers.app import Initializer
Initializer()
from openg2p_g2p_bridge_mapper_connectors.implementations import SPARMapper
from openg2p_g2p_bridge_mapper_connectors.schemas import ResolveRequest
async def main():
 result=await SPARMapper.get_component().resolve(ResolveRequest(beneficiary_ids=['NG-LAB-0001']))
 assert result and result.results and result.results[0].fa,result
 print('Bridge worker successfully resolved the signed synthetic beneficiary account.')
asyncio.run(main())
'''
r=subprocess.run(['kubectl','exec','-i','-n','nigeria','deploy/bridge-celery-worker','--','python','-'],input=script,text=True,capture_output=True)
print(r.stdout[-2000:]);print(r.stderr[-3500:]);r.check_returncode()
