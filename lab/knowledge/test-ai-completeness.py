import json,sys
from unittest.mock import patch,Mock
from flask import Flask
from werkzeug.exceptions import ServiceUnavailable
sys.path.insert(0,'/opt/openg2p-lab/registration')
import local_ai
response=Mock()
with Flask('test').app_context(),patch.object(local_ai.requests,'post',return_value=response):
 response.json.return_value={'done_reason':'length','message':{'content':json.dumps({'answer':'Incomplete'})}}
 try:local_ai.generate([],{})
 except ServiceUnavailable:pass
 else:raise AssertionError('Truncated generation was accepted')
 response.json.return_value={'done_reason':'stop','message':{'content':json.dumps({'answer':'A complete sentence.'})}}
 assert local_ai.generate([],{})['answer']=='A complete sentence.'
print('Truncated AI answer rejected; complete response accepted.')
