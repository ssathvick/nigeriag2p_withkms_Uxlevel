"""Create a destination-specific source tree; does not deploy or change services."""
import argparse,json,re,shutil
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--source',type=Path,required=True,help='Repository lab directory')
 p.add_argument('--destination',type=Path,required=True,help='New, empty Linux staging directory')
 p.add_argument('--config',type=Path,required=True,help='Copy of deployment.example.json')
 a=p.parse_args();source=a.source.resolve();dest=a.destination.resolve();config=json.loads(a.config.read_text())
 if not (source/'pbms-react/nsipa_approval/models.py').is_file():p.error('Source must be the current lab directory')
 if source==dest or source in dest.parents or dest in source.parents:p.error('Source and destination must be separate trees')
 if dest.exists() and any(dest.iterdir()):p.error('Destination must be empty; choose a new release directory')
 hosts=config['hostnames']
 for old,new in hosts.items():
  if not re.fullmatch(r'[A-Za-z0-9.-]+',old) or not re.fullmatch(r'[A-Za-z0-9.-]+',new):p.error('Hostname mappings must contain hostnames only, without a scheme or path')
 blocked={'node_modules','.git','.next','dist','build','__pycache__','.venv','evidence','backups','private','startup-logs'}
 text_ext={'.py','.js','.jsx','.ts','.tsx','.css','.html','.cjs','.mjs','.json','.xml','.md','.txt','.sh','.ps1','.bat','.conf','.svg','.yaml','.yml'}
 files=0;changed=0
 for src in sorted(source.rglob('*')):
  rel=src.relative_to(source)
  if not src.is_file() or any(x in blocked for x in rel.parts):continue
  if src.name.startswith('.env') and src.name!='.env.example':continue
  if src.name in {'credentials.yaml','credentials.yml','credentials.json','config.json','service.env'}:continue
  if src.name.endswith('.local.json') or src.name.endswith('.local.yaml'):continue
  if src.suffix in {'.key','.pem','.p12','.pfx','.sqlite','.db','.sql','.log'}:continue
  out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if src.suffix in text_ext or src.name.startswith('Dockerfile'):
   try:
    text=data.decode('utf-8-sig');before=text
    text=text.replace('/mnt/h/Nigeria_Mosip/codex/openg2p-lab',dest.as_posix())
    text=text.replace('/mnt/h/Nigeria_Mosip/codex',(dest.parent/'source-output').as_posix())
    for old,new in sorted(hosts.items(),key=lambda x:len(x[0]),reverse=True):text=text.replace(old,new)
    if before!=text:data=text.encode();changed+=1
   except UnicodeError:pass
  out.write_bytes(data);shutil.copymode(src,out);files+=1
 (dest/'release-preparation.json').write_text(json.dumps({'source':str(source),'files':files,'adapted_files':changed,'hostnames':hosts},indent=2))
 print(json.dumps({'destination':str(dest),'files':files,'adapted_files':changed,'deployed':False}))

if __name__=='__main__':main()
