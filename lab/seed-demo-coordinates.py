"""Explicitly requested synthetic household coordinates; preserves administrative fields."""
import sys,json,random,hashlib,datetime,os
from pathlib import Path
sys.path.insert(0,'/opt/openg2p-lab/registration')
import registration_app as r
root=Path('/opt/openg2p-lab/registration');geo=json.loads((root/'static/nigeria-states.geojson').read_text());states={f['properties']['id']:f for f in geo['features']}
def ring_contains(pt,ring):
 x,y=pt;inside=False
 for a,b in zip(ring,ring[1:]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
 return inside
def contains(pt,f):
 polys=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
 return any(ring_contains(pt,poly[0]) and not any(ring_contains(pt,hole) for hole in poly[1:]) for poly in polys)
def point(record,state):
 f=states[state];polys=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates'];coords=[q for poly in polys for q in poly[0]];xs=[q[0] for q in coords];ys=[q[1] for q in coords];rng=random.Random(hashlib.sha256(('nigeriag2p-demo-v1:'+str(record)).encode()).hexdigest())
 for _ in range(100000):
  pt=[round(rng.uniform(min(xs),max(xs)),6),round(rng.uniform(min(ys),max(ys)),6)]
  if contains(pt,f):return pt
 raise ValueError('Cannot place point within state')
backup=root/'geography-backups'/('demo-coordinates-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));backup.mkdir(mode=0o700)
with r.pg('register') as c:
 with c.cursor() as cur:
  cur.execute("SELECT h.internal_record_id,h.latitude,h.longitude,h.geo_code_hierarchy_json,g.state_id,h.geo_lowest_level_value_id,h.country_code,h.record_status FROM g2p_register_households h JOIN ng2p_record_geography g ON g.internal_record_id=h.internal_record_id AND g.record_type='household' ORDER BY h.internal_record_id FOR UPDATE OF h")
  rows=cur.fetchall();(backup/'household-location-before.json').write_text(json.dumps(rows,default=str));os.chmod(backup/'household-location-before.json',0o600)
  added=0
  for rid,lat,lon,hierarchy,state,area,country,status in rows:
   if lat is not None or lon is not None:continue
   if state not in states:continue
   lng,lat=point(rid,state);meta=dict(hierarchy or {});ng=dict(meta.get('nigeriag2p') or {});ng.update({'coordinate_source':'synthetic_demo','coordinate_verified':False,'coordinate_is_demo':True,'coordinate_scope':'state_only','accuracy_m':None,'demo_seed_version':1});meta['nigeriag2p']=ng
   cur.execute('UPDATE g2p_register_households SET latitude=%s,longitude=%s,geo_code_hierarchy_json=%s::jsonb WHERE internal_record_id=%s AND latitude IS NULL AND longitude IS NULL',(lat,lng,json.dumps(meta),rid));added+=cur.rowcount
  cur.execute("SELECT h.internal_record_id,h.latitude,h.longitude,h.geo_code_hierarchy_json,g.state_id,h.geo_lowest_level_value_id,h.country_code,h.record_status FROM g2p_register_households h JOIN ng2p_record_geography g ON g.internal_record_id=h.internal_record_id AND g.record_type='household' ORDER BY h.internal_record_id")
  after=cur.fetchall();assert len(after)==len(rows)
  for old,new in zip(rows,after):
   assert old[0]==new[0] and old[4:]==new[4:]
   if new[3].get('nigeriag2p',{}).get('coordinate_source')=='synthetic_demo':assert contains([new[2],new[1]],states[new[4]])
   else:assert old==new
print(json.dumps({'households_total':len(rows),'demo_coordinates_added':added,'state_structure_preserved':True,'all_demo_points_inside_assigned_state':True}))
