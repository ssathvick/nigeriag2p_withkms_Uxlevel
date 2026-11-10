"""Mock sessions verify missing/partial resolution never marks a native batch complete."""
import json,subprocess,sys
from pathlib import Path
code='''
from openg2p_g2p_bridge_celery_workers.app import Initializer
Initializer()
from openg2p_g2p_bridge_celery_workers.tasks.mapper_resolution_task import process_and_store_resolution
from unittest.mock import MagicMock
from types import SimpleNamespace as N
outcomes=[]
for name,rows in [('empty',[]),('partial',[N(id='A',fa={'account_number':'LAB-TEST'},name='Fictional')]),('unresolved',[N(id='A',fa=None,name='Fictional')])]:
 session=MagicMock()
 try:process_and_store_resolution('test-batch',N(results=rows),{'A':'test-a','B':'test-b'},session)
 except ValueError:outcomes.append(name)
 assert not session.commit.called,name
assert len(outcomes)==3
session=MagicMock();process_and_store_resolution('test-batch',N(results=[N(id='A',fa={'account_number':'LAB-TEST'},name='Fictional')]),{'A':'test-a'},session)
assert session.commit.called
print('PHASE1_NATIVE_GUARD_TESTS_PASSED')
'''
result=subprocess.run(['kubectl','-n','nigeria','exec','-i','deploy/bridge-celery-worker','--','python','-'],input=code,text=True,capture_output=True,timeout=30)
passed=result.returncode==0 and 'PHASE1_NATIVE_GUARD_TESTS_PASSED' in result.stdout
report={'scope':'Native installed mapper with mocked database sessions','checks':4,'status':'passed' if passed else 'failed','real_data_changed':False}
Path(__file__).with_name('phase1-evidence').joinpath('native-mapper-guard-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
sys.exit(0 if passed else 1)
