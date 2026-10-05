import json,pathlib,sys,subprocess,requests
sys.path.insert(0,'/mnt/h/Nigeria_Mosip/codex/openg2p-lab');from labdb import query
r=pathlib.Path('/opt/openg2p-lab');data=json.loads((r/'batch-pm-api.json').read_text())
for p in ['/partners/requests/onboarding','/partners/requests/{request_id}/approve','/partners/{partner_id}/disable']:
 b=data['paths'][p]['post'].get('requestBody',{});print(p,b)
for name,schema in data['components']['schemas'].items():
 if any(w in name.lower() for w in ['onboard','approve','request','keyinput']): print(name,schema)
ip=subprocess.check_output(['kubectl','get','svc','commons-services-awe','-n','nigeria','-o','jsonpath={.spec.clusterIP}'],text=True).strip()
a=requests.get('http://'+ip+'/v1/awe/openapi.json');print('awe schema',a.status_code)
if a.ok:
 data=a.json();(r/'batch-awe-api.json').write_text(json.dumps(data))
 for name,schema in data['components']['schemas'].items():
  if 'Submit' in name or 'CreateRequest' in name:print(name,schema)
print('Geos',query('master_data',"SELECT level_value_id,level_value_mnemonic FROM g2p_geo_level_values WHERE level_value_id LIKE 'NG%' ORDER BY level_value_id LIMIT 45;"))
