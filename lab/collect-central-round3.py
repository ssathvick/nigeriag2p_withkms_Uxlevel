import requests,json,concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
P=Path('territory-data/raw');urls={
'imo-leadership-seats':'https://imha.imostate.gov.ng/inauguration-of-the-assembly/',
'rivers-assembly-full':'https://hoa.rv.gov.ng/members.html',
'rivers-2025-members':'https://www.tvcnews.tv/17-rivers-house-of-assembly-members-defect-to-apc/',
'rivers-new-members':'https://leadership.ng/rivers-assembly-inaugurates-newly-elected-lawmakers/',
'rivers-reinstated':'https://www.premiumtimesng.com/news/headlines/918369-rivers-assembly-reinstates-three-pro-fubara-lawmakers.html',
'oyo-inauguration':'https://radionigeriaibadan.gov.ng/2023/06/14/ogundoyin-speaker-of-oyo-assembly-for-second-time/',
'oyo-officers':'https://radionigeriaibadan.gov.ng/2023/06/20/new-principal-officers-take-charge-at-oyha/',
'oyo-atiba-seat':'https://localgovernment.oyostate.gov.ng/2025/02/03/oyo-inaugurates-alaafins-coronation-committee/',
'oyo-school-visit':'https://pmparrotng.com/2026/06/19/from-promise-to-fulfillment-hon-yusuf-adebisi-inspects-site-for-first-secondary-school-in-his-constituency/',
'oyo-teacher-motion':'https://radionigeriaibadan.gov.ng/2023/11/29/lawmaker-calls-for-implementation-of-teachers-retirement-age/',
'oyo-budget-defence':'https://radionigeriaibadan.gov.ng/2023/12/13/lawmakers-embark-on-budget-defence-for-oyo-mdas/',
'imo-road-motion':'https://statesmannewspaper.com/imo-assembly-okays-motion-to-rehabilitate-emekuku-emii-ulakwo-road/'}
def fetch(it):
 key,url=it
 try:
  r=requests.get(url,timeout=25);r.raise_for_status();(P/('round3-'+key+'.html')).write_text(r.text);s=BeautifulSoup(r.text,'html.parser');txt=s.get_text(' ',strip=True);(P/('round3-'+key+'.txt')).write_text(txt);print(key,r.status_code,len(txt))
 except Exception as e:print(key,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(fetch,urls.items()))
(P/'central-round3-sources.json').write_text(json.dumps(urls,indent=2))
