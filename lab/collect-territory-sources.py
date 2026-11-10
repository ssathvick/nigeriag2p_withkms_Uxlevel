from pathlib import Path
import requests,json,concurrent.futures,subprocess
root=Path('/mnt/h/Nigeria_Mosip/codex/openg2p-lab/territory-data/raw');root.mkdir(parents=True,exist_ok=True)
urls={'mpi.pdf':'https://nigerianstat.gov.ng/pdfuploads/NIGERIA%20MULTIDIMENSIONAL%20POVERTY%20INDEX%20SURVEY%20RESULTS%202022.pdf','projects.pdf':'https://budgit.org/wp-content/uploads/2023/06/FG-2023-Project-.pdf'}
from territory_economy import URL as ECONOMY_URL
urls['worldbank-ndu-2025.pdf']=ECONOMY_URL
from territory_state_reports import REPORT_URLS
urls.update(REPORT_URLS)
def get(pair):
 name,url=pair;p=root/name
 if not p.exists():
  r=requests.get(url,timeout=90);r.raise_for_status();assert r.content.startswith(b'%PDF');p.write_bytes(r.content)
 subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True)
 return name,p.stat().st_size
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for x in pool.map(get,urls.items()):print(x)
for term in ['GRID3 NGA Operational LGA Boundaries','GRID3 NGA Health Facilities v2.0','GRID3 Nigeria Ward Boundaries']:
 r=requests.get('https://www.arcgis.com/sharing/rest/search',params={'q':term,'f':'json','num':12},timeout=30).json()
 print(json.dumps([{'id':x['id'],'title':x['title'],'url':x.get('url'),'owner':x['owner']} for x in r.get('results',[])],indent=2))
