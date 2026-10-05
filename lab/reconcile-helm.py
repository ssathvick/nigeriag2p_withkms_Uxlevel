#!/usr/bin/env python3
"""Preserve tested local networking, trust and package repairs on Helm upgrades."""
import yaml,sys,subprocess,os
sys.path.insert(0,os.path.dirname(__file__))
# Invoke existing de-duplication renderer before preserving runtime repairs.
render=subprocess.run(['python3','/mnt/h/Nigeria_Mosip/codex/openg2p-lab/post-render.py'],input=sys.stdin.read(),text=True,capture_output=True,check=True).stdout
docs=[d for d in yaml.safe_load_all(render) if d and d['kind']!='ServiceMonitor']
for d in docs:
 if not d:continue
 if d['kind']=='Secret':
  m=d['metadata'];r=subprocess.run(['kubectl','get','secret',m['name'],'-n',m.get('namespace','nigeria'),'-o','json'],text=True,capture_output=True)
  if r.returncode==0:
   import json
   existing=json.loads(r.stdout);d.pop('stringData',None);d['data']=existing.get('data',{});d['type']=existing.get('type','Opaque')
 if d['kind'] in ['Deployment','StatefulSet','VirtualService','Gateway']:
  m=d['metadata'];r=subprocess.run(['kubectl','get',d['kind'],m['name'],'-n',m.get('namespace','nigeria'),'-o','json'],text=True,capture_output=True)
  if r.returncode==0:
   import json
   d['spec']=json.loads(r.stdout)['spec']
yaml.safe_dump_all(docs,sys.stdout)
