/* IQS presentation theme. API payloads, URLs, identifiers and form values remain intact. */
(() => {
  'use strict';
  const brand = /open\s*g2p/gi;
  const root = '/iqs-brand/';
  const replace = text => text.split(/(https?:\/\/\S+|[A-Z]:\\[^\s]+|\/opt\/[^\s]+|[\w.+-]+@[\w.-]+\.[\w.-]+)/i).map((part,index) => index % 2 ? part : part.replace(/openg2p\.org/gi, 'iqs-solutions.com').replace(brand, 'NigeriaG2P')).join('');
  let queued = false;
  function update() {
    queued = false;
    if (!document.body) return;
    let title = replace(document.title);
    if (!/NigeriaG2P/i.test(title)) title = 'NigeriaG2P | ' + title;
    if (document.title !== title) document.title = title;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode: n => n.parentElement?.closest('script,style,code,pre,textarea,input,[contenteditable="true"],.monaco-editor') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT
    });
    let node;
    while ((node = walker.nextNode())) {
      if (/open\s*g2p/i.test(node.nodeValue)) {
        const next = replace(node.nodeValue);
        if (next !== node.nodeValue) node.nodeValue = next;
      }
    }
    document.querySelectorAll('[title],[alt],[aria-label],[placeholder]').forEach(el => {
      ['title','alt','aria-label','placeholder'].forEach(key => {
        const value = el.getAttribute(key);
        if (value && /open\s*g2p/i.test(value)) {
          const next = replace(value);
          if (next !== value) el.setAttribute(key,next);
        }
      });
    });
    document.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src') || '';
      const alt = img.getAttribute('alt') || '';
      if (src.startsWith(root)) return;
      if (/openg2p.*logo|logo.*openg2p|company_logo|g2p_theme.*(?:png|svg)|(?:^|\/)(?:logo(?:[_-](?:bw|horizontal|vertical|1))?(?:@2x)?\.(?:png|svg|webp))(?:\?|$)/i.test(decodeURIComponent(src)) || /^(?:registry\s+)?logo$|^IQS(?:\s+logo)?$|^OpenG2P\s+logo$/i.test(alt)) {
        img.removeAttribute('srcset');
        img.setAttribute('src', root + 'iqs-logo.png');
        img.setAttribute('alt','IQS — IQ Systems Solutions');
        img.classList.add('iqs-brand-logo');
      }
    });
    document.querySelectorAll('link[rel*="icon"]').forEach(link => {
      if (link.getAttribute('href') !== root+'iqs-logo.png') link.setAttribute('href',root+'iqs-logo.png');
    });
    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (/^https?:\/\/(?:www\.)?openg2p\.org(?:\/|$)/i.test(href)) link.setAttribute('href','https://iqs-solutions.com/');
    });
    const login = document.querySelector('form.oe_login_form, #kc-form-login, #kc-reset-password-form');
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
      if (document.title !== 'NigeriaG2P | Sign in') document.title = 'NigeriaG2P | Sign in';
      const card = login.closest('.card, .login-pf-page, .oe_website_login_container') || login.parentElement;
      card.classList.add('iqs-login-card');
      if (!card.querySelector('.iqs-login-heading')) {
        const heading = document.createElement('div');
        heading.className = 'iqs-login-heading';
        heading.innerHTML = '<div class="iqs-logo-mark" role="img" aria-label="IQS — IQ Systems Solutions"></div><div class="iqs-login-eyebrow">NIGERIA GOVERNMENT TO PEOPLE</div><h1>Welcome to NigeriaG2P</h1><p>Sign in to your programme workspace</p>';
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
