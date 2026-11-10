import sys,json
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab')
import jos_connected as j
j.init(r)
if sys.argv[1]=='prepare':print('Native Jos programme ID:',j.prepare(r))
elif sys.argv[1]=='snapshot':
 data=j.snapshot(r);j.publish(r,data);print(json.dumps(j.public_snapshot(data),indent=2,default=str))
else:print(j.operate(r,sys.argv[1],sys.argv[2],'authorized-synthetic-demo-setup'))
