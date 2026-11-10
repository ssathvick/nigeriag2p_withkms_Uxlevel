import sys,json
from pathlib import Path
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
import registration_app as r
import jos_connected as j
from flask import g
x=j.snapshot(r)
for row in x['rows']:
 stages=[j.minister_stage(row,i) for i in range(1,9)]
 with r.app.test_request_context('/registration/jos-cct/minister'):
  g.user={'name':'Render verification'};g.staff=True;g.session={'csrf':'render-only'}
  for stage in stages:
   html=r.page('jos-minister.html',data=x,row=row,stage=stage,stages=stages,panel=False,message='',error=False)
   assert 'SAMPLE BENEFICIARIES ONLY' in html and 'csrf' in html if stage['actions'] else 'SAMPLE BENEFICIARIES ONLY' in html
fresh=next(z for z in x['rows'] if z['id']=='JOS-NATIVE-002')
assert fresh['registry_status']!='complete' and not fresh['dispatch_started'] and fresh['bank']['credited_ngn']==0
assert j.minister_stage(fresh,1)['actions']==[('registry','Approve sample registration and synchronise')]
assert all(not j.minister_stage(fresh,n)['actions'] for n in range(2,9))
pending=next(z for z in x['rows'] if z['id']=='JOS-NATIVE-003')
assert not j.minister_stage(pending,5)['done'] and not j.minister_stage(pending,6)['actions']
client=r.app.test_client();resp=client.get('/registration/jos-cct/minister');assert resp.status_code==302 and 'minister=1' in resp.headers['Location']
print('PASS: 24 stage templates rendered; native stage gating; fresh sample remains untouched; login returns to minister route. No payment actions executed.')
