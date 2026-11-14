import requests
from pathlib import Path
u='https://www.crshoa.crossriverstate.gov.ng/assets/team-DL_XJCNo.js';s=requests.get(u,timeout=25).text;Path('territory-data/raw/cross-river-team-data.js').write_text(s);print(s)
