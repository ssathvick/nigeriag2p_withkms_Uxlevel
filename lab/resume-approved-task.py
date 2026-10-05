import subprocess
code='''import asyncio
from awe.db import init_engine, session_scope
from awe.models import ApprovalRequest, ApprovalTask
from awe.services.engine import apply_decision
async def main():
 init_engine()
 async with session_scope() as session:
  request=await session.get(ApprovalRequest,"700ca35f-d97d-4f6d-84e5-3be9d3a75049")
  task=await session.get(ApprovalTask,"73a21b34-c0d9-48c2-a0af-41a989166ccf")
  if request.current_stage_order==1 and task.status=="completed":
   task.status="open"
   await apply_decision(session,request,task,"Nigeria UX Admin","approve")
  print(request.status,request.current_stage_order)
asyncio.run(main())
'''
subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/commons-services-awe','--','python','-'],input=code,text=True,check=True)
