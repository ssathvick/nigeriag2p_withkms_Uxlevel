import requests,concurrent.futures,json
from pathlib import Path
from bs4 import BeautifulSoup
root=Path('territory-data/raw')
urls={'benue-assembly':'https://mio.benuestate.gov.ng/about-benue/house-of-assembly','anambra-assembly':'https://anambrastate.gov.ng/government/legislature/','delta-assembly':'https://deltastate.gov.ng/portfolio/legislator/','ekiti-assembly':'https://hoa.ekitistate.gov.ng/members.php','ekiti-new':'https://www.hoa.ek.gov.ng/','imo-assembly':'https://imha.imostate.gov.ng/','kano-assembly':'https://kanoassembly.gov.ng/10th-kano-state-house-of-assembly-members-2023-2027/','jigawa-assembly':'https://www.jigawastate.gov.ng/housemembers','osun-assembly':'https://osha.osunstate.gov.ng/allmembers','ondo-assembly':'https://www.ondostate.gov.ng/house_members','oyo-assembly':'https://oyostate.gov.ng/the-legislature/','rivers-assembly':'https://riversstate.gov.ng/government/legislature','zamfara-assembly':'https://zsha.zamfara.gov.ng/','yobe-assembly':'https://yobestate.gov.ng/legislature/','gombe-assembly':'https://gombestate.gov.ng/legislative-2/'}
(root/'assembly-source-urls.json').write_text(json.dumps(urls,indent=2))
def get(item):
 k,u=item
 try:
  r=requests.get(u,timeout=25);r.raise_for_status();(root/(k+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');t=s.get_text(' ',strip=True);(root/(k+'.txt')).write_text(t);print(k,len(t),t[:150]);print('LINKS',k,[(a.get_text(' ',strip=True),a.get('href')) for a in s.select('a[href]') if any(w in a.get_text().lower() for w in ['member','bill','proceeding'])][:15])
 except Exception as e:print(k,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(get,urls.items()))
