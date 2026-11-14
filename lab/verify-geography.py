import sys,json,csv
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r,nigeria_geography as geo
report=geo.summary(r);points=geo.household_points(r)
assert report['totals']=={'individual':215,'household':58}
assert all(row['zone_id'] and row['state_id'] for row in report['counts'])
assert points['metadata']['households_total']==58
assert points['metadata']['households_missing_coordinates']==0 and len(points['features'])==58
assert points['metadata']['demo_coordinate_count']==58
assert all(f['properties']['coordinate_is_demo'] and not f['properties']['coordinate_verified'] for f in points['features'])
out=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/geography')
with (out/'NigeriaG2P-Record-Counts-by-Location.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(report['counts'][0]));writer.writeheader();writer.writerows(report['counts'])
(out/'live-data-verification.json').write_text(json.dumps({'totals':report['totals'],'all_records_zone_state_resolved':True,'household_location_coverage':points['metadata']},indent=2))
print(json.dumps({'totals':report['totals'],'mapped_zone_and_state':True,'households_with_coordinates':58,'households_missing_coordinates':0,'demo_points':58}))
import requests
for path in ['health','api/geography/summary','api/geography/households.geojson','api/geography/areas']:
 response=requests.get('http://127.0.0.1:18081/registration/'+path,timeout=10)
 assert response.status_code==(401 if path in ['api/geography/summary','api/geography/households.geojson'] else 200)
 print(path,response.status_code)
