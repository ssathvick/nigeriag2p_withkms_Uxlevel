"""Prepare the NSIPA presentation theme, preserving integration identifiers."""
from pathlib import Path
import shutil, datetime, xml.etree.ElementTree as ET, copy, re

base=Path(__file__).resolve().parent
assets=base.parent/'NSIPA-Identity'
brand=base/'branding'
backup=base.parent/'outputs'/('nsipa-source-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
backup.mkdir(parents=True)
for folder in ['branding','persona-ui/src','sitewide-ui','registration-ui']:
    shutil.copytree(base/folder,backup/folder)
for source,target in [('NSIPA-primary-outlined.svg','nsipa-logo.svg'),('NSIPA-symbol-outlined.svg','nsipa-symbol.svg'),('NSIPA-primary.png','nsipa-logo.png'),('NSIPA-primary.png','iqs-logo.png')]:
    shutil.copy2(assets/source,brand/target)
# Recompose the approved emblem and outlined acronym for small navigation slots.
ET.register_namespace('','http://www.w3.org/2000/svg')
ns='{http://www.w3.org/2000/svg}'
original=ET.parse(assets/'NSIPA-primary-outlined.svg').getroot()
wordmark=ET.Element(ns+'svg',{'viewBox':'0 0 410 110','width':'410','height':'110'})
emblem=copy.deepcopy(original[0]);emblem.set('transform','translate(0 -1) scale(.4)');wordmark.append(emblem)
letters=copy.deepcopy(original[1]);letters.set('transform','translate(-149 -34) scale(.88)');wordmark.append(letters)
ET.ElementTree(wordmark).write(brand/'nsipa-wordmark.svg',encoding='utf-8',xml_declaration=True)

p=brand/'iqs-brand.js';s=p.read_text(encoding='utf-8')
s=s.replace('/* IQS presentation theme.', '/* NSIPA presentation theme.')
s=s.replace('const brand = /open\\s*g2p/gi;', "const brand = /open\\s*g2p|keycloak|\\bODK(?: Central)?\\b|IQ Systems Solutions|\\bIQS\\b(?![-_])|Nigeria\\s*G2P|iqs-solutions\\.com/gi;")
s=s.replace("part.replace(/openg2p\\.org/gi, 'iqs-solutions.com').replace(brand, 'NigeriaG2P')", "part.replace(/openg2p\\.org/gi, 'NSIPA').replace(brand, 'NSIPA')")
s=s.replace("if (!/NigeriaG2P/i.test(title)) title = 'NigeriaG2P | ' + title;", "if (!/NSIPA/i.test(title)) title = 'NSIPA | ' + title;")
s=s.replace("if (/open\\s*g2p/i.test(node.nodeValue)) {", "if (replace(node.nodeValue) !== node.nodeValue) {")
s=s.replace("if (value && /open\\s*g2p/i.test(value)) {", "if (value && replace(value) !== value) {")
# Match the original image attributes before replacing accessible brand names.
start=s.index("    document.querySelectorAll('img').forEach")
end=s.index('    // Change the ODK',start)
s=s[:start]+'''    document.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src') || '';
      const alt = img.getAttribute('alt') || '';
      if (/\\/nsipa-(?:logo|wordmark|symbol)\\.(?:svg|png)/.test(src)) return;
      let decoded = src; try { decoded = decodeURIComponent(src); } catch (_) {}
      const branded = /(?:openg2p|keycloak|odk|iqs)[^/]*(?:logo|favicon)|(?:logo|favicon)[^/]*(?:openg2p|keycloak|odk|iqs)|company_logo|g2p_theme.*(?:png|svg)|\\/(?:keycloak|odk|iqs-logo)\\.(?:png|svg)|(?:^|\\/)(?:logo(?:[_-](?:bw|horizontal|vertical|1))?(?:@2x)?\\.(?:png|svg|webp))(?:\\?|$)/i.test(decoded);
      if (branded || /^(?:(?:registry|NSIPA|IQS|OpenG2P|Keycloak|ODK)\\s+)?logo$|^(?:NSIPA|IQS|OpenG2P|Keycloak|ODK)(?:\\s*[—–-].*)?$/i.test(alt)) {
        img.removeAttribute('srcset');
        img.setAttribute('src', root + 'nsipa-wordmark.svg');
        img.setAttribute('alt','NSIPA — National Social Investment Programmes Agency');
        img.classList.add('iqs-brand-logo');
      }
    });
    let icons = document.querySelectorAll('link[rel*="icon"]');
    if (!icons.length) { const icon = document.createElement('link'); icon.rel='icon'; document.head.appendChild(icon); icons=[icon]; }
    icons.forEach(link => {
      if (link.getAttribute('href') !== root+'nsipa-symbol.svg') {
        link.setAttribute('href',root+'nsipa-symbol.svg'); link.setAttribute('type','image/svg+xml'); link.removeAttribute('sizes');
      }
    });
    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      // Corporate branding links only: authentication and service routes stay intact.
      if (/^https?:\\/\\/(?:www\\.)?(?:openg2p\\.org|iqs-solutions\\.com)(?:\\/|$)/i.test(href)) link.setAttribute('href','https://www.nsipa.gov.ng/');
      if (link.closest('.powered-by, .powered_by, footer, .footer') && /^https?:\\/\\/(?:www\\.)?(?:keycloak\\.org|getodk\\.org)(?:\\/|$)/i.test(href)) link.setAttribute('href','https://www.nsipa.gov.ng/');
    });
    // Inline SVG product logos used by administration consoles.
    document.querySelectorAll('svg[aria-label],svg[role="img"],svg.pf-v5-c-brand,svg.pf-c-brand').forEach(svg => {
      const label=(svg.getAttribute('aria-label')||'')+' '+(svg.querySelector('title')?.textContent||'');
      if (/keycloak|openg2p|\\bODK\\b|\\bIQS\\b/i.test(label)) {
        const img=document.createElement('img');img.src=root+'nsipa-wordmark.svg';img.alt='NSIPA';img.className='iqs-brand-logo';svg.replaceWith(img);
      }
    });
''' + s[end:]
s=s.replace('// Change the ODK Central product label only; leave help, attribution and form content intact.', '// Field data product branding; retain collection and authentication behaviour.')
s=s.replace('IQS Field Data','NSIPA Field Data')
s=s.replace("document.title.replace(/ODK Central/g, 'NSIPA Field Data')", "document.title.replace(/ODK Central/g, 'NSIPA Field Data')")
s=s.replace("#kc-form-login, #kc-reset-password-form", "#kc-form-login, #kc-reset-password-form, #kc-passwd-update-form, #kc-otp-login-form")
s=s.replace("'NigeriaG2P | Sign in'", "'NSIPA | Sign in'")
s=s.replace('aria-label="IQS — IQ Systems Solutions"','aria-label="NSIPA — National Social Investment Programmes Agency"')
s=s.replace('Welcome to NigeriaG2P','Welcome to NSIPA')
s=s.replace('NIGERIA GOVERNMENT TO PEOPLE','NATIONAL SOCIAL INVESTMENT PROGRAMMES AGENCY')
p.write_text(s,encoding='utf-8')

p=brand/'iqs-brand.css';s=p.read_text()
for old,new in {'#27166b':'#006b45','#fff200':'#d5a63c','#ede9fa':'#e7f1eb','#f4f2fb':'#f1f6f2','#fffbea':'#faf7ed','#e4e0ef':'#dce7df','#665f79':'#52675d','#6f6788':'#52675d','#d9d3e6':'#cbded1','#b9ade8':'#7ab49c','#3d2889':'#004e33','#39267c':'#006b45','#302848':'#123e31'}.items():s=s.replace(old,new)
s=s.replace("url('/iqs-brand/iqs-logo.png')", "url('/iqs-brand/nsipa-logo.svg')")
s += '''
/* NSIPA approved vector identity. Compact marks remain readable in navigation. */
.iqs-brand-logo{width:140px!important;height:46px!important;max-width:180px!important;max-height:64px!important;object-fit:contain!important}
.iqs-logo-mark{width:min(100%,320px);height:113px;margin:0 auto 14px}
.iqs-login .powered-by{display:flex!important;align-items:center!important;justify-content:center!important;gap:8px!important;margin-top:20px!important}
.iqs-login .powered-by .iqs-brand-logo{width:100px!important;height:30px!important}
.hub-brand,.ng2p-platform-brand{display:inline-flex!important;align-items:center!important}
.nsipa-nav-logo{display:block!important;width:148px!important;height:42px!important;object-fit:contain!important}
#ng2p-platform-bar .nsipa-nav-logo{width:112px!important;height:32px!important}
.wordmark .nsipa-nav-logo{width:160px!important;height:48px!important}
.brand img[src*="nsipa-"]{width:140px!important;height:48px!important;object-fit:contain!important}
body.ng2p-odk #app .navbar-brand::before{width:28px!important;height:28px!important;background-image:url('/iqs-brand/nsipa-symbol.svg')!important}
body.ng2p-odk #app .navbar-brand{height:38px!important}
.login-pf .kc-logo-text,#kc-logo-wrapper{background-image:url('/iqs-brand/nsipa-wordmark.svg')!important;background-size:contain!important;background-repeat:no-repeat!important}
@media(max-width:600px){.hub-header{flex-wrap:wrap;gap:14px}.nsipa-nav-logo{width:124px!important;height:36px!important}.iqs-logo-mark{height:98px}}
'''
p.write_text(s)

p=base/'persona-ui/src/site.jsx';s=p.read_text();s=s.replace('href="/">NigeriaG2P</a>','href="/" aria-label="NSIPA home"><img className="nsipa-nav-logo" src="/iqs-brand/nsipa-wordmark.svg" alt="NSIPA"/></a>');s=s.replace('NigeriaG2P','NSIPA');p.write_text(s)
p=base/'persona-ui/src/shell.js';s=p.read_text();s=s.replace("brand.textContent='NigeriaG2P';", "const logo=document.createElement('img');logo.src='/iqs-brand/nsipa-wordmark.svg';logo.alt='NSIPA';logo.className='nsipa-nav-logo';brand.appendChild(logo);brand.setAttribute('aria-label','NSIPA home');");s=s.replace('NigeriaG2P','NSIPA');p.write_text(s)
p=base/'persona-ui/src/main.jsx';s=p.read_text();s=s.replace('Nigeria<span>G2P</span>','<img className="nsipa-nav-logo" src="/iqs-brand/nsipa-wordmark.svg" alt="NSIPA"/>');s=s.replace('NigeriaG2P','NSIPA');p.write_text(s)
for p in [base/'persona-ui/src/catalogue.js',base/'sitewide-ui/modules.json']:
    s=p.read_text().replace('in ODK Central.','in NSIPA Field Data.');p.write_text(s)
p=base/'sitewide-ui/index.html';s=p.read_text().replace('NigeriaG2P','NSIPA').replace('phase1-20261012','nsipa-20261103');p.write_text(s)
for p in (base/'registration-ui').glob('*.html'):
    s=p.read_text();s=s.replace('/iqs-brand/iqs-logo.png','/iqs-brand/nsipa-wordmark.svg').replace('IQS — IQ Systems Solutions','NSIPA — National Social Investment Programmes Agency').replace('IQS Nigeria','NSIPA Nigeria').replace('NigeriaG2P','NSIPA')
    p.write_text(s)
print('NSIPA source theme and vector assets prepared. Backup:',backup)
