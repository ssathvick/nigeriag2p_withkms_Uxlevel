from pathlib import Path
from bs4 import BeautifulSoup
import re
p=Path('territory-data/raw')
for key,term in [('ngf-current','Abia State Governor'),('ekiti-members','Aribasoye'),('imo-members','OLEMGBE'),('osun-assembly','Egbedun'),('benue-assembly','Emberga'),('rivers-assembly','Iderima')]:
 s=BeautifulSoup((p/(key+'.html')).read_text(),'html.parser');n=s.find(string=lambda t:t and term in t);print('\n'+key,str(n.parent.parent.parent)[:3500])
s=(p/'ondo-assembly.html').read_text();print('ONDO SCRIPTS',re.findall(r'<script[^>]*src=["\']([^"\']+)',s));print('ONDO API',re.findall(r'.{0,100}(?:fetch\(|ajax|\.json).{0,180}',s))
s=BeautifulSoup((p/'ogun-activities.html').read_text(),'html.parser');print('OGUN EVIDENCE',[(a.get_text(' ',strip=True),a['href']) for a in s.select('a[href]') if any(w in a.get_text().lower() for w in ['oversight visit','financial documents','stakeholders','budget defence'])][:10])
