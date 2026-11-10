import requests,json,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw');events=json.loads((P/'northern-activity-next.json').read_text())
urls={e['source_url'] for e in events}|{'https://www.radionigeriakaduna.gov.ng/2026/10/01/nigeria-66-niger-speaker-congratulates-niger-people-nigerians/'}
def get(u):
 try:
  r=requests.get(u,timeout=20);r.raise_for_status();key=u.strip('/').split('/')[-1];(P/(key+'.html')).write_text(r.text);(P/(key+'.txt')).write_text(BeautifulSoup(r.text,'html.parser').get_text(' ',strip=True));print('saved',key)
 except Exception as e:print(e)
urls.update({'https://www.channelstv.com/2026/10/05/defected-lawmakers-were-suspended-long-before-leaving-apc-zamfara-speaker/','https://www.theconclaveng.com/maikasuwa-dangoje-emerges-kebbi-assembly-speaker/amp/'})
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(get,urls))
