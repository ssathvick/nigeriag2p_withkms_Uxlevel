from pathlib import Path
import subprocess
p=Path('/etc/nginx/sites-available/iqs-public');s=p.read_text();anchor=' root /opt/openg2p-lab/public-home;';assert s.count(anchor)==1
if 'location ^~ /field-preview/' not in s:
 backup=p.with_name(p.name+'.field-preview.bak');backup.write_text(s)
 s=s.replace(anchor,anchor+"\n location = /field-preview { return 308 https://nigeriag2p.com/field-preview/; }\n location ^~ /field-preview/ {\n  sub_filter '</head>' '</head>';\n  add_header Cache-Control \"no-cache\";\n  try_files $uri $uri/ =404;\n }")
 p.write_text(s)
 try:subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
 except Exception:p.write_text(backup.read_text());subprocess.run(['systemctl','reload','nginx']);raise
print('Preview route isolated.')
