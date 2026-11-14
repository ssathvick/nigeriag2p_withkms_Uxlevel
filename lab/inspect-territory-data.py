import json
from pathlib import Path
for name in ['lga.geojson','health-counts.json']:
 d=json.load(open('territory-data/raw/'+name));print(name,'features',len(d.get('features',[])),'error',d.get('error'),'transfer',d.get('exceededTransferLimit'));print(d.get('features',[{}])[0].get('properties') or d.get('features',[{}])[0].get('attributes'))
text=Path('territory-data/raw/mpi.txt').read_text();parts=text.split('\f');print([(i+1,'D7' if 'D7. Multidimensional' in p else 'D6') for i,p in enumerate(parts) if 'D7. Multidimensional' in p or 'D6. Multidimensional' in p])
