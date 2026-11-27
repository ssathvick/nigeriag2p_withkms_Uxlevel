(() => {
  'use strict';

  const hostname = location.hostname;
  const config = window.NSIPAKnowledgeConfig;
  const configuredService = config?.services?.[hostname];
  const supported = config ? !!configuredService : /(^|\.)nigeriag2p\.com$/.test(hostname) ||
    /^g2p(?:-[a-z0-9-]+)?\.wverve\.in$/.test(hostname) || hostname === 'pbms.openg2p.localhost';
  const legacy = window.NG2PKnowledgeContext;
  const contextual = window.NSIPAContextualHelp;
  if (!supported || !legacy || window.top !== window.self || document.getElementById('ng-km-launcher')) return;

  const serviceName = configuredService || hostname.split('.')[0].replace(/^g2p-/, '');
  const platform = config?.platform || (hostname.endsWith('wverve.in') ? 'https://g2p.wverve.in' : 'https://nigeriag2p.com');
  const docs = config?.docs || 'https://docs.g2p.wverve.in';
  const root = platform + '/registration';
  const referenceOrigins = new Set([platform, docs, 'https://docs.openg2p.org',
    'https://nigeriag2p.com', 'https://g2p.wverve.in']);
  const roles = {all:'All users', citizen:'Citizen', officer:'Registration officer', verifier:'Verification officer',
    supervisor:'Programme supervisor', field:'Field Agent', level1:'First Reviewer', level2:'Second Reviewer',
    admin:'Registry Administrator', payment:'Payment', finance:'Finance', audit:'Audit', ceo:'CEO', 'pbms-admin':'Programme Admin'};
  const legacyRoles = ['all','citizen','officer','verifier','supervisor'];
  const element = (tag, value) => {
    const node = document.createElement(tag);
    if (value) node.textContent = value;
    return node;
  };
  function selectLabel(text, control) {
    const label = element('label', text);
    control.setAttribute('aria-label', text);
    label.append(control);
    return label;
  }
  const launcher = element('button', 'ⓘ Help');
  launcher.id = 'ng-km-launcher';
  launcher.type = 'button';
  launcher.setAttribute('aria-expanded', 'false');
  launcher.setAttribute('aria-controls', 'ng-km-panel');
  const panel = element('section');
  panel.id = 'ng-km-panel';
  panel.hidden = true;
  panel.lang = 'en';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Workflow help');
  const close = element('button', 'Close');
  close.className = 'ng-km-close';
  close.type = 'button';
  const header = element('div');
  header.className = 'ng-km-header';
  header.append(element('h2', 'Contextual help'), close);
  const content = element('div');
  content.className = 'ng-km-content';
  const note = element('p');
  note.id = 'ng-km-context';
  note.setAttribute('aria-live', 'polite');
  const articleBody = element('div');
  const browse = element('details');
  const serviceSelect = element('select'), roleSelect = element('select'), stageSelect = element('select');
  const follow = element('button', 'Follow current screen');
  follow.type = 'button';
  follow.className = 'ng-km-follow';
  for (const role of legacyRoles) roleSelect.add(new Option(roles[role], role));
  browse.append(element('summary', 'Browse other guidance'), selectLabel('Service', serviceSelect),
    selectLabel('Guidance role', roleSelect), selectLabel('Workflow stage', stageSelect), follow);
  const library = element('a', 'Open knowledge library');
  library.href = root + '/knowledge';
  content.append(note, articleBody, browse, library);
  panel.append(header, content);
  document.body.append(launcher, panel);

  let articles = [], articleRequest, identityGeneration = 0, identityPending = false, signedRole, openedFrom = launcher, targetField;
  let browsing = false, opening = false, anchor = null, timer, lastKey = '', route = location.href;
  const excluded = node => !!node?.closest?.('#ng-km-panel,#ng-km-launcher,#ng2p-platform-guide,#ng2p-platform-bar');
  const visible = node => !!node && node.getClientRects().length > 0 && !node.closest('[hidden],[aria-hidden="true"]') &&
    getComputedStyle(node).visibility !== 'hidden';
  const words = value => (value || '').replace(/ⓘ/g, '').replace(/\s+/g, ' ').trim();
  const headingText = node => words(node?.textContent);
  const onImportsPage = () => serviceName === 'register' && /\/data-imports(?:\/|$)/.test(location.pathname);
  const isImportFile = control => control.type === 'file' && control.name === 'file' && onImportsPage();
  function registryScopeNote() {
    if (serviceName !== 'register') return;
    const hints = [
      [/^Your records only\./, 'field'], [/^Level 1 review:/, 'level1'], [/^Level 2 review:/, 'level2'],
      [/^MBR Officer:/, 'officer'], [/^MBR Admin:/, 'admin']
    ];
    for (const note of document.querySelectorAll('aside[role="note"]')) {
      const match = hints.find(([pattern]) => pattern.test(headingText(note)));
      if (match && visible(note)) return match[1];
    }
  }
  function fieldLabel(control) {
    const associated = control.labels?.[0] || control.closest('label');
    const native = control.closest('.registry-native-form [data-section-id]');
    const groupedChoice = associated && ['radio','checkbox'].includes(control.type);
    if (!native || (associated && !groupedChoice)) return associated;
    // Native Registry widgets render labels beside their input wrappers.
    let wrapper = control.parentElement;
    for (let depth = 0; depth < 4 && wrapper && wrapper !== native; depth++, wrapper = wrapper.parentElement) {
      const caption = [...wrapper.querySelectorAll(':scope > label')].find(label =>
        groupedChoice ? !label.querySelector('input') : true);
      if (caption) return caption;
    }
    return associated;
  }
  function labelText(control) {
    if (!control) return '';
    if (isImportFile(control)) return 'Choose a beneficiary data file';
    if (control.name === 'consent_status') return 'Consent to share data';
    if (control.getAttribute('aria-label')) return words(control.getAttribute('aria-label'));
    const label = fieldLabel(control);
    if (label) {
      const copy = label.cloneNode(true);
      copy.querySelectorAll('input,select,textarea,button').forEach(node => node.remove());
      const text = words(copy.textContent).replace(/\s*\*$/, '');
      if (text) return text;
    }
    const container = control.parentElement;
    const sibling = container?.querySelector(':scope > label,:scope > span,:scope > div:first-child');
    return words(sibling?.textContent).replace(/\s*\*$/, '');
  }
  function shownButton(scope, names, activeOnly = false) {
    return [...(scope || document).querySelectorAll('button')].some(button =>
      visible(button) && (!activeOnly || !button.disabled) && names.includes(headingText(button)));
  }
  function signIn() {
    return [...document.querySelectorAll('input[type="password"]')].some(visible) &&
      !document.querySelector('.sidebar nav, .registry-workspace');
  }
  async function loadIdentity() {
    const generation = ++identityGeneration;
    signedRole = undefined;
    identityPending = false;
    if (signIn() || !['register','pbms'].includes(serviceName)) return;
    identityPending = true;
    let role;
    try {
      if (serviceName === 'register') {
        const options = {credentials:'same-origin', cache:'no-store'};
        let response = await fetch('/api/me',options);
        if (!response.ok && ![401,403].includes(response.status)) {
          await new Promise(resolve => setTimeout(resolve,150));
          if (generation !== identityGeneration || signIn()) return;
          response = await fetch('/api/me',options);
        }
        const identity = response.ok ? await response.json() : {};
        if (Object.hasOwn(roles,identity.registry_scope)) role = identity.registry_scope;
      } else if (document.querySelector('.sidebar nav')) {
        const model = 'g2p.beneficiary.list', method = 'nsipa_identity';
        const response = await fetch('/web/dataset/call_kw/' + model + '/' + method, {
          method:'POST', credentials:'same-origin', cache:'no-store', headers:{'Content-Type':'application/json'},
          body:JSON.stringify({jsonrpc:'2.0', method:'call', params:{model, method, args:[], kwargs:{}}, id:1})
        });
        const {result} = response.ok ? await response.json() : {};
        if (result) {
          const assigned = (result.roles || []).map(value => value.toLowerCase()).filter(value => Object.hasOwn(roles,value));
          role = result.admin ? 'pbms-admin' : result.payment ? 'payment' : assigned.length === 1 ? assigned[0] : undefined;
        }
      }
    } catch {
      // Current screen markers can still identify the role when identity is unavailable.
    }
    if (generation === identityGeneration) {
      identityPending = false;
      if (!signIn()) signedRole = role;
    }
  }
  function contextFor(target, control) {
    const screen = document.querySelector('[data-km-screen]');
    const dialogs = [...document.querySelectorAll('[role="dialog"],[role="alertdialog"],.modal.show,.o_dialog')].filter(node => !excluded(node) && visible(node));
    // An explicit Help trigger follows its own surface. The main launcher follows
    // the topmost dialog, including a report opened over an approval list.
    const explicitTarget = control || target;
    const modal = explicitTarget && serviceName === 'pbms' ?
      dialogs.findLast(dialog => dialog.contains(explicitTarget)) : dialogs.at(-1);
    const area = target?.closest('[data-km-stage]') || (modal && (modal.closest('[data-km-stage]') || modal.querySelector('[data-km-stage]'))) || screen;
    const heading = target?.closest('h1,h2,h3,h4,legend,summary,strong[data-km-import-receipt]');
    const parentSection = (control || target)?.closest('section,[data-section-id]');
    const section = headingText(heading || parentSection?.querySelector('h1,h2,h3,h4,legend'));
    const data = screen?.dataset || {};
    const selectedTab = document.querySelector('nav[aria-label="Data Imports"] [aria-current="page"]');
    const importsPage = onImportsPage();
    const importMain = importsPage ? document.querySelector('main') : undefined;
    const importConnected = !!importMain && shownButton(importMain, ['Fetch and validate']);
    const importChooseFetch = !!importMain && [...importMain.querySelectorAll('[role="alert"]')].some(node =>
      visible(node) && /^More than one import from this source may match\./i.test(headingText(node)));
    const importSharedFetch = !!importMain && [...importMain.querySelectorAll('[role="status"]')].some(node =>
      visible(node) && /^(?:New CSV import created\.|The separate CSV import already exists\.)/i.test(headingText(node)));
    const importFetchError = !!importMain && (importConnected || shownButton(importMain, ['Fetch a new CSV'])) &&
      [...importMain.querySelectorAll('[role="alert"]')].some(node =>
      visible(node) && /^(?:Could not (?:fetch the connected CSV|confirm the connected CSV fetch)|The source API did not return a CSV file|This source connection is unavailable|Choose an active connected source|The source connection (?:is missing its server credential|requires a valid HTTPS endpoint)|The connected source returned a file larger than 2 MB|Data Imports is temporarily unavailable|Unexpected (?:token|end).*JSON|Failed to fetch)/i.test(headingText(node)));
    const batchHeader = importsPage ? [...document.querySelectorAll('main button')]
      .find(button => visible(button) && headingText(button) === '← Back to imports')?.closest('section') : undefined;
    const importRowConflict = !!batchHeader && [...importMain.querySelectorAll('[role="alert"]')].some(node =>
      visible(node) && (node.hasAttribute('data-import-row-conflict') ||
        /^Some rows already have a Registry receipt or an in-progress transfer\./i.test(headingText(node))));
    const importTransferConflict = !!batchHeader && shownButton(batchHeader, ['Transfer to Registry','Retry transfer']) &&
      [...importMain.querySelectorAll('[role="alert"]')].some(node =>
        visible(node) && /^This batch changed\. Reload it and try again\./i.test(headingText(node)));
    const flowHeadings = [...document.querySelectorAll('.approval-demo > section h2,.approval-demo .demo-panel h2')].filter(visible);
    const stats = [...(modal?.querySelectorAll('.workflow-stats > div') || [])];
    const listStat = name => headingText(stats.find(node => headingText(node.querySelector('small')) === name)?.querySelector('strong'));
    const listStatus = listStat('Status');
    const correctionRecorded = listStatus === 'Returned for correction' && contextual?.correctionSinceReturn?.(
      listStat('Revision'), [...modal.querySelectorAll('.demo-history > strong')].map(headingText));
    const actionScope = modal || document;
    const role = signIn() ? 'all' : signedRole || registryScopeNote() || data.kmPersona || 'all';
    const paymentReportFields = serviceName === 'pbms' ? [...(modal?.querySelectorAll('dt') || [])] : [];
    const reportCount = label => {
      const field = paymentReportFields.find(node => label.test(headingText(node)));
      const value = headingText(field?.nextElementSibling);
      if (!/^(?:\d+|\d{1,3}(?:,\d{3})+)$/.test(value)) return undefined;
      const count = Number(value.replace(/,/g, ''));
      return Number.isSafeInteger(count) ? count : undefined;
    };
    const reversedCount = reportCount(/disbursements reversed/i);
    const reconciledCount = reportCount(/disbursements reconciled/i);
    const declaredCount = reportCount(/disbursements declared/i);
    const duplicateTab = serviceName === 'register' && [...document.querySelectorAll('button.bg-primary-first')]
      .find(button => visible(button) && /^(Intake|Existing) Duplicates$/.test(words(button.firstChild?.textContent)));
    const paymentContext = serviceName === 'pbms' ? {
      paymentSubmitted:dialogs.some(dialog => shownButton(dialog,['View payment progress'])),
      paymentRoutingMissing:[...(modal?.querySelectorAll('p') || [])]
        .some(p => /^Programme Admin must configure sponsor bank routing/i.test(headingText(p))),
      paymentReportFields:paymentReportFields.map(headingText),
      paymentReportReversed:reversedCount > 0,
      paymentReportReversalMismatch:reversedCount > reconciledCount,
      paymentReportReversalAmountException:reportCount(/reversal amount exceptions/i) > 0,
      paymentReportPartial:reconciledCount > 0 && reconciledCount <= declaredCount &&
        (reconciledCount < declaredCount || (reversedCount > 0 && reversedCount < reconciledCount)),
      paymentReportPending:[...(modal?.querySelectorAll('[role="status"]') || [])]
        .some(node => /payment status record is not yet available/i.test(headingText(node)))
    } : {};
    const input = {
      ...paymentContext,
      service:serviceName, path:location.pathname, hash:location.hash, role, section,
      registryPageState:serviceName === 'register' ? headingText([...document.querySelectorAll('main.application-state h1')].find(visible)) : '',
      configurationNav:serviceName === 'register' && !!target?.closest('nav[aria-label="Configuration sections"]'),
      duplicateView:duplicateTab ? (words(duplicateTab.firstChild.textContent) === 'Intake Duplicates' ? 'duplicates-intake' : 'duplicates-register') : undefined,
      returnedIntake:serviceName === 'register' && [...document.querySelectorAll('section h2')]
        .some(node => visible(node) && headingText(node) === 'Review feedback'),
      sectionId:(control || target)?.closest('[data-section-id]')?.getAttribute('data-section-id'),
      field:labelText(control), signIn:signIn(), dialog:modal?.getAttribute('aria-label') || '',
      explicitStage:area?.dataset.kmStage, tab:headingText(selectedTab), flowHeading:headingText(flowHeadings[0]),
      listStatus, correctionRecorded, canDecideList:shownButton(actionScope, ['Approve and save','Reject and save'], true),
      canSubmitList:shownButton(actionScope, ['Initiate approval','Resubmit for approval'], true),
      correctList:shownButton(actionScope, ['Correct','Save correction'], true),
      exportList:shownButton(actionScope, ['Export Beneficiaries (.xls)'], true),
      canPayList:shownButton(actionScope, ['Proceed to payments'], true),
      canRouteList:shownButton(actionScope, ['Save payment routing']),
      assignedIntakeTask:serviceName === 'register' && /\/tasks\/intake-form\/?$/.test(location.pathname) &&
        [...document.querySelectorAll('span[title="open" i],span[title="claimed" i]')].some(visible),
      canReview:shownButton(document, ['Approve','Reject permanently','Revalidate — return to field agent'], true),
      intakeEditor:shownButton(document, ['Save Draft','Submit']) || !!document.querySelector('.registry-native-form form'),
      intakeSection:!!target?.closest('[data-section-id]'),
      recordEditor:!!document.querySelector('[data-section-id$="-edit"]'),
      denied:importsPage && [...document.querySelectorAll('h2')].some(n => visible(n) && headingText(n) === 'Access to Data Imports'),
      batch:!!batchHeader,
      importConnected, importChooseFetch, importFetchError, importSharedFetch, importTransferConflict, importRowConflict,
      importStatus:headingText(batchHeader?.querySelector('span[data-tone]')),
      importReceivedWithError:!!batchHeader?.querySelector('[data-import-received-with-error="true"]'),
      importSavedWithoutLog:!!batchHeader?.querySelector('[data-import-saved-without-log="true"]'),
      importReceiptLogRestored:!!batchHeader?.querySelector('[data-import-receipt-log-restored="true"]'),
      return:!!batchHeader && shownButton(batchHeader, ['Approve batch']),
      correct:!!batchHeader && shownButton(batchHeader, ['Send for approval']),
      transfer:!!batchHeader && shownButton(batchHeader, ['Transfer to Registry']),
      retry:!!batchHeader && shownButton(batchHeader, ['Retry transfer']),
      importRowField:importsPage && section === 'Reconcile records' && control?.type === 'text' && !!control.closest('details form')
    };
    const mapped = contextual?.resolve(input);
    if (mapped) return {...mapped, audience:role, contextual:true};
    const legacyRole = legacyRoles.includes(role) ? role : 'all';
    const guess = legacy.resolve({
      hostname:configuredService || hostname, path:input.path, hash:input.hash, persona:legacyRole,
      view:data.kmView, status:data.kmStatus, dialog:!!modal,
      explicit:area?.dataset.kmModule && area.dataset.kmStage ? {module:area.dataset.kmModule, stage:area.dataset.kmStage} : undefined,
      section:section || headingText(document.querySelector('[role="tab"][aria-selected="true"],.tabs .active,.o_notebook .nav-link.active')),
      heading:headingText(document.querySelector('main h1'))
    });
    return guess;
  }

  async function load() {
    if (!articleRequest) {
      articleRequest = fetch('/iqs-brand/knowledge?audience=all&include_roles=1', {credentials:'omit', cache:'no-store'})
        .then(response => {
          if (!response.ok) throw Error('Help unavailable');
          return response.json();
        }).then(data => {
          articles = data.articles;
          serviceSelect.replaceChildren(...data.modules.map(module => new Option(module.name,module.id)));
        }).catch(error => {
          articleRequest = undefined;
          throw error;
        });
    }
    return articleRequest;
  }
  function appendSection(heading, value) {
    if (value?.trim()) articleBody.append(element('h4', heading), element('p', value));
  }
  function render(article, field, related = [], fieldHelp) {
    articleBody.replaceChildren();
    if (!article && !field && !fieldHelp) {
      articleBody.append(element('p', 'No task-specific guidance is available for this screen.'));
      return;
    }
    const shown = field || article || {};
    content.scrollTop = 0;
    if (shown.provisional || fieldHelp) {
      const status = element('p','Provisional sandbox guidance · Business validation pending');
      status.className = 'ng-km-note';
      articleBody.append(status);
    }
    articleBody.append(element('h3',fieldHelp?.label || shown.title),
      element('p',fieldHelp?.description || shown.purpose));
    if ((field || fieldHelp) && article) {
      const screenLink = element('button','Show screen help');
      screenLink.textContent = article.help_level === 'workflow' ? 'Show workflow guide' : 'Show screen help';
      screenLink.type = 'button';
      screenLink.addEventListener('click', () => render(article, undefined, related));
      articleBody.append(screenLink);
    } else if (!field && !fieldHelp) {
      const steps = (article.steps || '').split('\n').filter(line => line.trim());
      if (steps.length) {
        const list = element('ol');
        for (const line of steps) list.append(element('li',line));
        articleBody.append(list);
      }
      appendSection('Before you start',article.requirements);
      appendSection('What happens next',article.next_step);
      appendSection('Common issues',article.issues);
    }
    if (shown.scope === 'upstream_reference') articleBody.append(element('p','Upstream reference. Confirm availability in this installation.'));
    const references = [...(shown.sources || [])];
    const documentationTopic = shown.visibility === 'public' && shown.scope === 'local_workflow' &&
      /^context-(imports|register)-([a-z0-9]+(?:-[a-z0-9]+)*)$/.exec(shown.context_key);
    if (documentationTopic) {
      references.unshift({
        title: 'Open documentation guide',
        url: docs + '/topics/' + documentationTopic[1] + '/' + documentationTopic[2] + '/',
      });
    }
    if (references.length) {
      const refs = element('ul');
      for (const {title,url} of references) {
        let target;
        try { target = new URL(url); } catch { continue; }
        if (target.username || target.password || (!referenceOrigins.has(target.origin) &&
          !(target.origin === 'https://github.com' && target.pathname.startsWith('/OpenG2P/openg2p-documentation/')))) continue;
        const link = element('a',title);
        link.href = url;
        link.rel = 'noopener noreferrer';
        link.target = '_blank';
        const item = element('li');
        item.append(link);
        refs.append(item);
      }
      if (refs.children.length) articleBody.append(element('h4','References'),refs);
    }
    articleBody.append(element('small','Version ' + shown.version));
    const links = [...new Map(related.filter(item => item?.id && item.id !== shown.id && item.id !== article?.id).map(item => [item.id,item])).values()];
    if (links.length) {
      const more = element('details'), list = element('ul');
      more.append(element('summary','Related guidance'));
      for (const item of links) {
        const li = element('li'), link = element('a',item.title);
        link.href = root + '/knowledge/' + item.id;
        li.append(link);
        list.append(li);
      }
      more.append(list);
      articleBody.append(more);
    }
    library.href = root + '/knowledge/' + shown.id;
  }
  const bySlug = slug => articles.find(item => (item.context_key || item.slug) === slug);
  function matchesStage(module, stage, audience, allowUpstream) {
    return articles.filter(item => item.module === module && item.stage === stage && ['all', audience].includes(item.audience) &&
      item.help_level !== 'field' && (allowUpstream || item.scope !== 'upstream_reference'))
      .sort((a,b) => Number(b.audience === audience) - Number(a.audience === audience) ||
        Number(!!b.context_key) - Number(!!a.context_key) || b.version - a.version)[0];
  }
  function choices(module, audience, selected) {
    const items = new Map();
    for (const entry of articles) {
      if (entry.module !== module || !['all',audience].includes(entry.audience) || entry.help_level === 'field') continue;
      const previous = items.get(entry.stage);
      if (!previous || entry.id === selected || (previous.id !== selected && (entry.audience !== previous.audience && entry.audience === audience ||
          entry.audience === previous.audience && entry.context_key && !previous.context_key))) items.set(entry.stage, entry);
    }
    return [...items.values()].sort((a,b) => a.title.localeCompare(b.title));
  }
  function showChoices(module, audience, selected) {
    serviceSelect.value = module;
    roleSelect.value = legacyRoles.includes(audience) ? audience : 'all';
    stageSelect.replaceChildren(...choices(module,roleSelect.value,selected).map(item => new Option(item.title,item.id)));
    stageSelect.value = selected || '';
  }
  function sync(force = false) {
    if (panel.hidden || browsing || identityPending || (opening && !force) || !articles.length) return;
    if (anchor && !anchor.isConnected) anchor = null;
    if (targetField && !targetField.isConnected) targetField = null;
    const current = contextFor(anchor,targetField);
    const key = JSON.stringify(current);
    if (!force && key === lastKey) return;
    lastKey = key;
    const group = current.slug?.match(/^context-(register|imports|pbms)-/)?.[1];
    const workflow = group && bySlug('context-' + group + (group === 'pbms' ? '-flow-journey' : '-journey'));
    const screen = bySlug(current.slug) || matchesStage(current.module,current.stage,current.audience,false) ||
      (!current.contextual && matchesStage(current.module,current.stage,current.audience,true)) ||
      (!current.contextual && matchesStage(current.module,'Service overview',current.audience,false)) || workflow;
    const field = targetField ? bySlug(current.fieldSlug) : undefined;
    const related = (current.related || []).map(item => matchesStage(item.module,item.stage,current.audience,true));
    if (current.contextual) {
      if (current.slug.startsWith('context-pbms-payment-report-partial')) {
        related.push(bySlug('context-pbms-partial-payment-workflow'),
          bySlug('context-pbms-reversal-amount-discrepancy-workflow'));
      } else if (current.slug.startsWith('context-pbms-payment-report-reversal-amount-exception')) {
        related.push(bySlug('context-pbms-reversal-amount-discrepancy-workflow'),
          bySlug('context-pbms-late-reversal-case-reopening-workflow'));
      } else if (current.slug.startsWith('context-pbms-payment-report-reversal-mismatch')) {
        related.push(bySlug('context-pbms-duplicate-reversal-workflow'),
          bySlug('context-pbms-reversal-amount-discrepancy-workflow'),
          bySlug('context-pbms-late-reversal-case-reopening-workflow'));
      } else if (current.slug.startsWith('context-pbms-payment-report-reversal')) {
        related.push(bySlug('context-pbms-corrective-payment-workflow'),
          bySlug('context-pbms-corrective-reversal-workflow'),
          bySlug('context-pbms-escalation-further-payment-workflow'),
          bySlug('context-pbms-escalation-case-closure-workflow'),
          bySlug('context-pbms-duplicate-reversal-workflow'),
          bySlug('context-pbms-reversal-amount-discrepancy-workflow'),
          bySlug('context-pbms-late-reversal-case-reopening-workflow'),
          bySlug('context-pbms-reopened-case-payment-workflow'));
      }
      if (workflow) related.push(workflow);
    }
    const level = field || current.fieldHelp ? 'Field help' : screen?.help_level === 'workflow' ? 'Workflow guide' :
      !current.contextual && screen?.stage === 'Service overview' ? 'Service guide' : 'Screen help';
    const importRoles = {level1:'Approver · Registry First Reviewer',field:'Operator · Registry Field Agent',admin:'Administrator · Registry Administrator'};
    const audienceName = onImportsPage() && importRoles[current.audience] ||
      (serviceName === 'register' && current.audience === 'officer' ? 'MBR Officer' : roles[current.audience]);
    note.textContent = level + ' · ' + (audienceName || roles.all);
    showChoices(current.module,current.audience,screen?.id);
    render(screen,field,related,current.fieldHelp);
  }
  function hide() {
    panel.hidden = true;
    launcher.setAttribute('aria-expanded','false');
    if (openedFrom.isConnected) openedFrom.focus();
  }
  async function open(source, control, sectionHeading) {
    openedFrom = source;
    anchor = source === launcher ? null : sectionHeading || source;
    targetField = control;
    browsing = false;
    opening = true;
    lastKey = '';
    panel.hidden = false;
    launcher.setAttribute('aria-expanded','true');
    note.textContent = '';
    articleBody.replaceChildren(element('p','Loading guidance…'));
    try {
      await Promise.all([load(),loadIdentity()]);
      if (!panel.hidden) {
        sync(true);
        close.focus();
      }
    } catch {
      articleBody.replaceChildren(element('p','Help is temporarily unavailable. Try the knowledge library.'));
    } finally {
      opening = false;
    }
  }
  function browseSelection() {
    browsing = true;
    note.textContent = 'Browsing other guidance';
    const selected = articles.find(item => String(item.id) === stageSelect.value);
    render(selected,undefined,selected ? legacy.relatedGuides(selected).map(item => matchesStage(item.module,item.stage,roleSelect.value,true)) : []);
  }
  function addHelp(parent, label, control, sectionButton) {
    const trigger = element('button','ⓘ');
    trigger.type = 'button';
    trigger.className = 'ng-km-inline';
    trigger.title = control ? 'Help for this field' : 'Help for this section';
    trigger.setAttribute('aria-label','Help: ' + label);
    trigger.addEventListener('click',event => {
      event.preventDefault();
      event.stopPropagation();
      void open(trigger,control,sectionButton ? parent : undefined);
    });
    if (sectionButton) sectionButton.after(trigger);
    else if (control) parent.after(trigger);
    else parent.append(trigger);
  }
  function decorate() {
    for (const heading of document.querySelectorAll('h1,h2,h3,h4,legend')) {
      if (serviceName === 'register' && heading.closest('a[href]')) continue;
      const sectionButton = serviceName === 'register' && heading.closest('button,[role="button"]');
      if (sectionButton && sectionButton.nextElementSibling?.classList.contains('ng-km-inline')) continue;
      if (excluded(heading) || !visible(heading) || heading.closest('header,aside,nav') && !heading.closest('main') ||
          heading.querySelector(':scope > .ng-km-inline')) continue;
      const label = headingText(heading);
      if (label) addHelp(heading,label,undefined,sectionButton);
    }
    if (onImportsPage()) {
      for (const label of document.querySelectorAll('main summary, main section strong')) {
        const title = headingText(label);
        if (!visible(label) || label.querySelector(':scope > .ng-km-inline') ||
            !['Expected columns','Test mapping with sample values','Registry receipt'].includes(title)) continue;
        if (label.tagName === 'STRONG') label.setAttribute('data-km-import-receipt','');
        addHelp(label,title);
      }
    }
    if (!contextual || !['register','pbms','keycloak','g2p','nigeriag2p'].includes(serviceName)) return;
    const controls = document.querySelectorAll('form input#username,form input[name="login"],main input,main select,main textarea,.registry-native-form input,.registry-native-form select,.registry-native-form textarea,[role="dialog"] input,[role="dialog"] select,[role="dialog"] textarea');
    for (const control of controls) {
      const labelNode = fieldLabel(control) || control;
      if (excluded(control) || control.dataset.kmFieldDecorated ||
          (!visible(control) && !(isImportFile(control) && visible(labelNode)))) continue;
      const label = labelText(control);
      const fieldContext = contextFor(control,control);
      if (!label || !(fieldContext.fieldSlug || fieldContext.fieldHelp)) continue;
      control.dataset.kmFieldDecorated = '1';
      if (control.name === 'consent_status') {
        const group = control.closest('[data-section-id]');
        if (group?.querySelector('button[aria-label="Help: Consent to share data"]')) continue;
      }
      if (labelNode.nextElementSibling?.getAttribute('aria-label') !== 'Help: ' + label) addHelp(labelNode,label,control);
    }
  }
  function schedule() {
    if (timer !== undefined) return;
    timer = setTimeout(() => {
      timer = undefined;
      decorate();
      sync();
    },100);
  }
  close.addEventListener('click',hide);
  panel.addEventListener('keydown',event => { if (event.key === 'Escape') { event.preventDefault(); hide(); } });
  launcher.addEventListener('click',() => panel.hidden ? open(launcher) : hide());
  stageSelect.addEventListener('change',browseSelection);
  for (const select of [serviceSelect,roleSelect]) select.addEventListener('change',() => {
    const items = choices(serviceSelect.value,roleSelect.value);
    stageSelect.replaceChildren(...items.map(item => new Option(item.title,item.id)));
    browseSelection();
  });
  follow.addEventListener('click',() => { browsing = false; anchor = null; targetField = null; browse.open = false; sync(true); });
  let sessionMarker = sessionContext();
  function sessionContext() {
    return JSON.stringify([location.href, signIn(), registryScopeNote(), !!document.querySelector('.sidebar nav')]);
  }
  function refreshContext(force = false) {
    const marker = sessionContext();
    if (!force && marker === sessionMarker) return;
    sessionMarker = marker;
    ++identityGeneration;
    signedRole = undefined;
    anchor = targetField = null;
    browsing = false;
    browse.open = false;
    lastKey = '';
    if (!panel.hidden) {
      note.textContent = '';
      articleBody.replaceChildren(element('p','Loading guidance…'));
      void loadIdentity().then(() => sync(true));
    }
    schedule();
  }
  new MutationObserver(records => {
    if (records.some(record => !excluded(record.target.nodeType === 1 ? record.target : record.target.parentElement))) {
      refreshContext();
      schedule();
    }
  }).observe(document.body,{childList:true,subtree:true,attributes:true,
    attributeFilter:['hidden','disabled','aria-current','aria-selected','aria-pressed','data-km-stage','data-km-status','data-km-persona','data-km-view']});
  window.addEventListener('pbms-session-expired',() => refreshContext(true));
  window.addEventListener('pageshow',event => { if (event.persisted) refreshContext(true); });
  window.addEventListener('popstate',() => refreshContext());
  window.addEventListener('hashchange',() => refreshContext());
  window.setInterval(() => { if (route !== location.href) { route = location.href; refreshContext(); } },300);
  decorate();
})();
