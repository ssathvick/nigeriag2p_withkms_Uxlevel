/* NSIPA presentation theme. API payloads, URLs, identifiers and form values remain intact. */
(() => {
  'use strict';
  const brand = /open\s*g2p(?![._-])|keycloak|\bSuperset\b|\bMinIO\b|\bOdoo\b|\bRedpanda\b|\bODK(?: Central)?\b|IQ Systems Solutions|\bIQS\b(?![-_])|Nigeria\s*G2P|iqs-solutions\.com/gi;
  const root = '/iqs-brand/';
  const replace = text => text.split(/(https?:\/\/\S+|[A-Z]:\\[^\s]+|\/opt\/[^\s]+|[\w.+-]+@[\w.-]+\.[\w.-]+)/i).map((part,index) => index % 2 ? part : part.replace(/openg2p\.org/gi, 'NSIPA').replace(/\bSuperset\b/gi, 'NSIPA Analytics').replace(brand, 'NSIPA')).join('');
  let queued = false;
  function update() {
    queued = false;
    if (!document.body) return;
    let title = replace(document.title);
    if (!/NSIPA/i.test(title)) title = 'NSIPA | ' + title;
    if (document.title !== title) document.title = title;
    // Inline SVG product logos used by administration consoles.
    document.querySelectorAll('svg[aria-label],svg[role="img"],svg.pf-v5-c-brand,svg.pf-c-brand').forEach(svg => {
      const label=(svg.getAttribute('aria-label')||'')+' '+(svg.querySelector('title')?.textContent||'');
      if (/keycloak|openg2p|\bODK\b|\bIQS\b/i.test(label)) {
        const img=document.createElement('img');img.src=root+'nsipa-wordmark.svg';img.alt='NSIPA';img.className='iqs-brand-logo';svg.replaceWith(img);
      }
    });
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: n => n.parentElement?.closest('script,style,code,pre,textarea,input,[contenteditable="true"],.monaco-editor') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    });
    const isFieldData = /^(?:odk)\./.test(location.hostname);
    let node;
    while ((node = walker.nextNode())) {
      if (replace(node.nodeValue) !== node.nodeValue || (isFieldData && /\bCentral\b|NSIPA Docs website/.test(node.nodeValue))) {
        const next = replace(node.nodeValue).replace(isFieldData ? /\bCentral\b|NSIPA Docs website/g : /$^/g, value => value === 'Central' ? 'NSIPA Field Data' : 'field-data documentation website');
        if (next !== node.nodeValue) node.nodeValue = next;
      }
    }
    document.querySelectorAll('[title],[alt],[aria-label],[placeholder]').forEach(el => {
      ['title','alt','aria-label','placeholder'].forEach(key => {
        const value = el.getAttribute(key);
        if (value && replace(value) !== value) {
          const next = replace(value);
          if (next !== value) el.setAttribute(key,next);
        }
      });
    });
    document.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src') || '';
      const alt = img.getAttribute('alt') || '';
      if (/\/nsipa-(?:logo|wordmark|symbol)\.(?:svg|png)/.test(src)) return;
      if (/^staff-portal\./.test(location.hostname) && img.closest('.grid.grid-cols-4')) {
        img.removeAttribute('srcset'); img.src=root+'nsipa-symbol.svg'; img.alt='NSIPA'; img.classList.add('nsipa-service-logo'); return;
      }
      let decoded = src; try { decoded = decodeURIComponent(src); } catch (_) {}
      const branded = /(?:openg2p|keycloak|odk|iqs|superset|minio|redpanda|odoo)[^/]*(?:logo|favicon)|(?:logo|favicon)[^/]*(?:openg2p|keycloak|odk|iqs|superset|minio|redpanda|odoo)|company_logo|g2p_theme.*(?:png|svg)|\/(?:keycloak|odk|iqs-logo)\.(?:png|svg)|(?:^|\/)(?:logo(?:[_-](?:bw|horizontal|vertical|1))?(?:@2x)?\.(?:png|svg|webp))(?:\?|$)/i.test(decoded);
      if (branded || /^(?:(?:registry|NSIPA|IQS|OpenG2P|Keycloak|ODK)\s+)?logo$|^(?:NSIPA|IQS|OpenG2P|Keycloak|ODK)(?:\s*[—–-].*)?$/i.test(alt)) {
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
      if (/^https?:\/\/(?:www\.)?(?:openg2p\.org|iqs-solutions\.com)(?:\/|$)/i.test(href)) link.setAttribute('href','https://www.nsipa.gov.ng/');
      if (link.closest('.powered-by, .powered_by, footer, .footer') && /^https?:\/\/(?:www\.)?(?:keycloak\.org|getodk\.org)(?:\/|$)/i.test(href)) link.setAttribute('href','https://www.nsipa.gov.ng/');
    });
    // Field data product branding; retain collection and authentication behaviour.
    if (['g2p-odk.wverve.in', 'odk.openg2p.localhost'].includes(location.hostname)) {
      const odkBrand = document.querySelector('#app .navbar-brand');
      if (odkBrand && odkBrand.textContent.trim() !== 'NSIPA Field Data') odkBrand.textContent = 'NSIPA Field Data';
      const brandedTitle = document.title.replace(/ODK Central/g, 'NSIPA Field Data');
      if (document.title !== brandedTitle) document.title = brandedTitle;
    }
    // Replace only the registry landing illustration, not record or profile images.
    if (['g2p-register.wverve.in', 'register.openg2p.localhost'].includes(location.hostname) && /^\/(?:en|fr|de|es)?\/?$/.test(location.pathname)) {
      const hero = document.querySelector('img[alt="Peoples"], img[data-iqs-registry-hero]');
      if (hero && !hero.hasAttribute('data-iqs-registry-hero')) {
        hero.setAttribute('data-iqs-registry-hero', 'true');
        hero.removeAttribute('srcset');
        hero.setAttribute('src', root + 'nigeria-registry-community.png');
        hero.setAttribute('alt', 'Nigerian community members using digital public services');
      }
    }
    const login = document.querySelector('form.oe_login_form, #kc-form-login, #kc-reset-password-form, #kc-passwd-update-form, #kc-otp-login-form');
    if (login && !login.querySelector('.iqs-mobile-info-link')) {
      const link = document.createElement('a');
      link.className = 'iqs-mobile-info-link';
      link.href = 'https://g2p.wverve.in/registration/mobile';
      link.textContent = 'Mobile apps';
      link.style.cssText = 'display:block;margin:16px 0;color:#155d50;font-weight:600';
      login.appendChild(link);
    }
    if (location.hostname === 'beneficiary.openg2p-ux.localhost' && /\/login\/?$/.test(location.pathname)) {
      const demoLink = document.querySelector('a[href*="getLoginProviderRedirect/4"]');
      if (demoLink && !document.querySelector('.iqs-beneficiary-login-note')) {
        const note = document.createElement('p');
        note.className = 'iqs-beneficiary-login-note';
        note.textContent = 'Demo account: choose SIGN IN TO LOCAL DEMO below, then enter fatima and the lab password on the next screen. The Email or Phone form above uses a different login method.';
        demoLink.parentElement.insertBefore(note,demoLink);
      }
    }
    if (login) {
      document.body.classList.add('iqs-login');
      if (document.title !== 'NSIPA | Sign in') document.title = 'NSIPA | Sign in';
      const card = login.closest('.card, .login-pf-page, .oe_website_login_container') || login.parentElement;
      card.classList.add('iqs-login-card');
      if (!card.querySelector('.iqs-login-heading')) {
        const heading = document.createElement('div');
        heading.className = 'iqs-login-heading';
        heading.innerHTML = '<div class="iqs-logo-mark" role="img" aria-label="NSIPA — National Social Investment Programmes Agency"></div><div class="iqs-login-eyebrow">NATIONAL SOCIAL INVESTMENT PROGRAMMES AGENCY</div><h1>Welcome to NSIPA</h1><p>Sign in to your programme workspace</p>';
        card.insertBefore(heading, card.firstChild);
      }
    }
  }
  function schedule() {
    if (!queued) { queued = true; requestAnimationFrame(update); }
  }
  function start() {
    update();
    new MutationObserver(schedule).observe(document.documentElement,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['src','srcset','alt','title','aria-label','placeholder']});
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();

