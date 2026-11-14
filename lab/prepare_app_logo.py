from pathlib import Path
root=Path(__file__).parent
p=root/'persona-ui/src/mbr.jsx';s=p.read_text()
s=s.replace('<span className="mbr-logo">N</span><span><strong>NSIPA</strong><small>Social Registry · MBR</small></span>', '<img className="mbr-logo" src="/iqs-brand/nsipa-logo.svg?v=user-vector-20261112" alt="NSIPA"/><span className="mbr-product"><small>Social Registry · MBR</small></span>')
p.write_text(s)
p=root/'persona-ui/src/mbr.css';s=p.read_text();marker='/* Supplied NSIPA vector logo */'
if marker not in s:s+='\n'+marker+'\n#mbr-root .mbr-logo{display:block;width:86px;height:64px;object-fit:contain;background:transparent;border-radius:0}#mbr-root .mbr-product{font-weight:600}@media(max-width:760px){#mbr-root .mbr-logo{width:74px;height:54px}#mbr-root .mbr-product{display:none}}\n'
p.write_text(s)
p=root/'pbms-react/src/main.jsx';s=p.read_text();s=s.replace('<b>N</b><span>NSIPA<br/><small>Nigeria social protection</small></span>','<img className="nsipa-product-logo" src="/iqs-brand/nsipa-logo.svg?v=user-vector-20261112" alt="NSIPA"/><span><small>Nigeria social protection</small></span>');s=s.replace('<b>N</b><span>NSIPA<small>Programme & Benefits</small></span>','<img className="nsipa-product-logo" src="/iqs-brand/nsipa-logo.svg?v=user-vector-20261112" alt="NSIPA"/><span><small>Programme & Benefits</small></span>');p.write_text(s)
for p in (root/'pbms-react/src').glob('*.css'):
 s=p.read_text()
 if '.nsipa-product-logo{' not in s:s+='\n.nsipa-product-logo{display:block;width:86px;height:64px;object-fit:contain;flex-shrink:0;background:#fff;border-radius:7px;padding:4px}\n'
 p.write_text(s)
p=root/'branding/SOURCE.md';p.write_text('Application logo supplied by the user: H:/Nigeria_Mosip/logo/NSIPA-Logo-Vector.svg. Adopted across the G2P application on 12 November 2026. The original SVG is retained as nsipa-original-supplied.svg. Application SVG variants preserve the artwork paths and colors, with the viewport fitted to the artwork for readable navigation. PNG compatibility assets are rendered from that same vector. See replacement-logo-source.json for the source checksum.\n')
for name in ['phase1-public.html','jos-connected.html']:
 p=root/'registration-ui'/name;s=p.read_text();s=s.replace('<a class="brand" href="/">NSIPA</a>','<a class="brand" href="/"><img src="/iqs-brand/nsipa-logo.svg?v=user-vector-20261112" alt="NSIPA"/></a>');s=s.replace('<a class="jc-brand" href="/jos-cct/">NSIPA / JOS CCT</a>','<a class="jc-brand" href="/jos-cct/"><img src="/iqs-brand/nsipa-logo.svg?v=user-vector-20261112" alt="NSIPA"/><span>Jos CCT</span></a>');p.write_text(s)
