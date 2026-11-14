import sys,json,sqlite3,hashlib
from pathlib import Path
from urllib.parse import quote
sys.path.insert(0,'/opt/openg2p-lab/odk-sync');from odk_sync_worker import Client,ROOT
from odk_household_mapping import parse_xml
out=ROOT/'legacy-review';out.mkdir(mode=0o700,exist_ok=True);client=Client(json.loads((ROOT/'config.json').read_text()))
c=sqlite3.connect(ROOT/'ledger.sqlite');c.row_factory=sqlite3.Row;rows=c.execute("SELECT * FROM imports WHERE state='QUARANTINED' AND error='Unapproved form or mismatched form version'").fetchall();results=[]
try:
 for row in rows:
  row=dict(row);prefix='/v1/projects/1/forms/'+row['form_id'];xml=client.get(prefix+'/submissions/'+quote(row['instance_id'],safe='')+'.xml').content;data=parse_xml(xml);version=data.get('version');(out/(row['instance_id'].replace(':','_')+'.xml')).write_bytes(xml)
  vals={}
  def walk(node,path=''):
   if len(node)==0:vals[path+'/'+node.tag]=node.text
   for child in node:walk(child,path+'/'+node.tag)
  walk(data)
  print(json.dumps({'instance':row['instance_id'],'version':version,'fields':vals}))
  r=client.odk.get(client.origin+prefix+'/versions/'+quote(version or '',safe='')+'.xml',timeout=30)
  if r.ok:(out/('definition-'+str(version)+'.xml')).write_bytes(r.content)
  print('definition fetch',r.status_code)
  results.append({'instance':row['instance_id'],'version':version,'source_sha256':hashlib.sha256(xml).hexdigest(),'definition_status':r.status_code})
 (out/'inventory.json').write_text(json.dumps(results,indent=2))
finally:client.close()
