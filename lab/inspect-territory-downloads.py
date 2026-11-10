import requests,json
from pathlib import Path
root=Path('territory-data/raw')
u='https://inecnigeria.org/wp-content/uploads/2024/02/2023-GENERAL-ELECTION-REPORT-1.pdf'
r=requests.get(u,timeout=40);print('INEC non-www',r.status_code,len(r.content))
if r.content.startswith(b'%PDF'):(root/'inec.pdf').write_bytes(r.content)
u='https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/2020/NGA/'
r=requests.get(u,timeout=30);print('WorldPop directory',r.status_code,r.text[:3500])
