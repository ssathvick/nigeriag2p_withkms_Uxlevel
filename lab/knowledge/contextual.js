(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.NSIPAContextualHelp = factory();
})(typeof globalThis === 'undefined' ? this : globalThis, function () {
  'use strict';

  const context = (group, key, field) => ({
    module: group === 'imports' ? 'register' : group,
    slug: 'context-' + group + '-' + key,
    fieldSlug: field ? 'context-' + group + '-' + field : undefined
  });

  function registrySection(heading, id) {
    if (/administrative location|household location|coordinates/i.test(heading)) return 'location';
    const sectionIds = {
      hh_survey_consent: 'consent', hh_composition_headship: 'headship', hh_members: 'members',
      hh_dwelling_services: 'conditions', hh_income_shocks: 'income', hh_health_insurance: 'vulnerability',
      hh_possessions: 'assets', hh_crops: 'assets', hh_table_assets: 'assets',
      hh_table_program_enrolments: 'programmes', hh_roster: 'members'
    };
    if (sectionIds[id]) return sectionIds[id];
    const types = [
      [/consent|enumeration/i, 'consent'],
      [/location|geograph|coordinates/i, 'location'],
      [/headship/i, 'headship'],
      [/members?|roster|composition/i, 'members'],
      [/income|employment|livelihood/i, 'income'],
      [/vulnerab|health|disab/i, 'vulnerability'],
      [/assets?|crops?|livestock/i, 'assets'],
      [/household programmes/i, 'programmes'],
      [/identity|identif|personal|contact|demograph/i, 'identity'],
      [/housing|dwelling|living condition|sanitation|water/i, 'conditions']
    ];
    return types.find(([pattern]) => pattern.test(heading))?.[1];
  }

  function imports(s) {
    const field = [
      [/^data source$/i, 'source-choice'], [/^choose a beneficiary data file\b/i, 'file-choice'],
      [/^reason for returning this batch$/i, 'return-note'], [/^exclude this row from the transfer$/i, 'exclude-row'],
      [/^issues and exclusions only$/i, 'issues-filter'],
      [/^(?:source name|source to configure)$/i, 'mapping-source'],
      [/^(?:destination register|native import template)$/i, 'mapping-destination'],
      [/^how to receive records$/i, 'mapping-connection'],
      [/^available for new imports$/i, 'mapping-availability'],
      [/^(?:spreadsheet column|registry column)$/i, 'mapping-columns'],
      [/^(?:transform|required value)$/i, 'mapping-rules'],
      [/^field for duplicate checks$/i, 'mapping-duplicate-key']
    ].find(([pattern]) => pattern.test(s.field))?.[1] || (s.importRowField ? 'source-row-value' : undefined);
    if (s.denied) return context('imports', 'denied');
    if (!s.batch && s.section === 'Transfer history') return context('imports', 'transfers');
    if (s.importRowConflict && !/^activity$/i.test(s.section)) {
      const guides = {field:'duplicate-receipt-field', level1:'duplicate-receipt-review', admin:'duplicate-receipt-admin'};
      return context('imports', guides[s.role] || 'duplicate-receipt', field);
    }
    if (/reconcile records|mapped registry values|source values/i.test(s.section)) return context('imports', 'reconcile', field);
    if (/^activity$/i.test(s.section)) return context('imports', 'activity');
    if (s.section === 'Expected columns') return context('imports', 'expected-columns');
    if (s.section === 'Test mapping with sample values') return context('imports', 'test-mapping');
    if (s.return || s.section === 'Review decision' || field === 'return-note') return context('imports', 'review', field);
    const partial = s.batch && s.importStatus === 'Partially ingested';
    const receiptAfterFailure = s.batch && s.importStatus === 'Ingested by Registry' && s.importReceivedWithError;
    const partialGuides = {field: 'partial-field', level1: 'partial-review', admin: 'partial-admin'};
    if (s.batch && s.importSavedWithoutLog && (!s.section || s.section === 'Registry receipt')) {
      return context('imports', 'receipt-log-missing');
    }
    if (s.batch && s.importReceiptLogRestored && (!s.section || s.section === 'Registry receipt')) {
      return context('imports', 'receipt-log-restored');
    }
    if (partial && s.section === 'Registry receipt') return context('imports', partialGuides[s.role] || 'partial');
    if (receiptAfterFailure && s.section === 'Registry receipt') return context('imports', 'receipt-after-job-failure');
    if (s.importChooseFetch) return context('imports', 'choose-fetch', field);
    if (s.batch) {
      if (s.importTransferConflict) return context('imports', 'transfer-conflict', field);
      if (s.importFetchError) return context('imports', 'fetch-error', field);
      if (s.importSharedFetch && s.importStatus === 'Draft') return context('imports', 'shared-fetch', field);
      const states = {
        'Draft': 'prepare', 'Awaiting approval': 'awaiting-review',
        'Returned for correction': s.correct ? 'correct' : 'returned-read',
        'Approved': s.transfer ? 'ready' : 'approved-read',
        'Submitting to Registry': 'submitting', 'Ready to retry': s.retry ? 'retry' : 'retry-read',
        'Submission unconfirmed': 'unconfirmed', 'Queued at Registry': 'queued',
        'Ingested by Registry': receiptAfterFailure ? 'receipt-after-job-failure' : 'receipt',
        'Partially ingested': partialGuides[s.role] || 'partial',
        'Ingestion needs attention': 'failed'
      };
      return context('imports', states[s.importStatus] || 'batch', field);
    }
    if (s.tab === 'New import' && s.importConnected) {
      return context('imports', s.importFetchError ? 'fetch-error' : 'fetch', field);
    }
    const tabs = {'New import': 'start', 'Sources and mappings': 'source', 'Access': 'access'};
    const byRole = {field: 'operator', level1: 'approver', admin: 'admin'};
    return context('imports', tabs[s.tab] || byRole[s.role] || 'transfers', field);
  }

  const registrySettings = new Map([
    ['registry/details', 'registry-details'],
    ['registry/languages', 'registry-languages'],
    ['registry/themes', 'registry-themes'],
    ['registry/themes/create', 'theme-create'],
    ['registry/users', 'staff'],
    ['data-models', 'data-models'],
    ['data-policies', 'data-policies'],
    ['data-policies/new', 'policy-create'],
    ['awe-policy-config', 'approval-policies'],
    ['registers', 'register-definitions'],
    ['intake-forms', 'form-definitions'],
    ['ingest-configurations/key-paths', 'ingest-paths'],
    ['ingest-configurations/manage-subscription', 'ingest-subscriptions'],
    ['ingest-configurations/semantic-patterns', 'ingest-patterns'],
    ['ingest-configurations/templates', 'ingest-templates'],
    ['outgest-configurations/templates', 'outgoing-templates'],
    ['outgest-configurations/topics', 'outgoing-topics'],
  ]);

  const registryDashboardSections = new Map([
    ['Register your household', 'registration-start'],
    ['Master Registry', 'published-registers'],
    ['Form submissions', 'submission-queues'],
    ['Change requests', 'change-queue'],
    ['My tasks', 'review-dashboard'],
    ['From capture to master record', 'journey'],
  ]);

  const offlineSections = new Map([
    ['Prepare your device', 'offline-device'],
    ['Connect to this registry', 'offline-device'],
    ['Download before you travel', 'offline-device'],
    ['Set up your device', 'offline-device'],
    ['Capture and check the interview', 'offline-delivery'],
    ['Reconnect and confirm delivery', 'offline-delivery'],
    ['One review workflow', 'journey'],
    ['Corrections and rejected records', 'returned-intake'],
  ]);

  function registryConfiguration(path, s) {
    if (s.configurationNav) return 'configuration-navigation';
    if (path === 'registry/users') {
      if (s.section === 'Onboard a staff member') return 'staff-onboarding';
      if (s.section === 'Independent responsibilities') return 'staff-responsibilities';
    }
    if (path === 'data-policies/new' && /^filter (rules|preview)$/i.test(s.section)) return 'policy-filters';
    const exact = registrySettings.get(path);
    if (exact) return exact;
    const details = [
      [/^registers\/[^/]+$/, 'register-structure'],
      [/^registers\/[^/]+\/sections\/[^/]+$/, 'register-section'],
      [/^registers\/[^/]+\/tabs\/[^/]+$/, 'register-tab'],
      [/^registers\/[^/]+\/scores\/[^/]+$/, 'register-score'],
      [/^intake-forms\/[^/]+$/, 'form-tabs'],
      [/^intake-forms\/[^/]+\/tabs\/[^/]+$/, 'form-sections']
    ];
    return details.find(([pattern]) => pattern.test(path))?.[1] || 'setup';
  }

  function registry(s) {
    const path = s.path.replace(/^\/[a-z]{2}(?:-[a-z]{2})?(?=\/|$)/i, '').replace(/\/$/, '') || '/';
    if (s.registryPageState === 'Access restricted') return context('register', 'state-restricted');
    if (s.registryPageState === 'Page not found') return context('register', 'state-missing');
    if (s.registryPageState === 'We could not load this page') return context('register', 'state-error');
    if (/^\/data-imports(?:\/|$)/.test(path)) return imports(s);
    const duplicateGuide = !s.field && (!s.section || /duplicate|^match\s*#/i.test(s.section)) ? s.duplicateView : undefined;
    if (/^\/tasks\/intake-form\/?$/.test(path)) {
      const guide = {level1:'review-l1', level2:'review-l2'}[s.role];
      return context('register', (s.assignedIntakeTask && guide) || 'intake-queue');
    }
    if (/^\/tasks\/intake-form\//.test(path)) {
      const key = duplicateGuide || (/duplicate/i.test(s.section) ? 'duplicates' :
        s.role === 'level1' && s.canReview ? 'review-l1' : s.role === 'level2' && s.canReview ? 'review-l2' : 'review-intake');
      return context('register', key, /message|reason/i.test(s.field) ? 'decision-note' : undefined);
    }
    if (/^\/tasks\/change-request\/?$/.test(path)) return context('register', 'change-task-queue');
    if (/^\/tasks\/change-request\//.test(path)) return context('register', 'change-detail');
    const intake = path.match(/^\/intake-form\/(household|individual)(?:\/(new|submission)\/[^/]+)?$/);
    if (intake) {
      if (!intake[2]) return context('register', 'submission-queues');
      if (duplicateGuide) return context('register', duplicateGuide);
      if (intake[2] === 'submission' && s.canReview && ['level1','level2'].includes(s.role)) {
        return context('register', s.role === 'level1' ? 'review-l1' : 'review-l2',
          /message|reason/i.test(s.field) ? 'decision-note' : undefined);
      }
      if (intake[2] === 'submission' && !s.intakeEditor) {
        return context('register', /duplicate/i.test(s.section) ? 'duplicates' : 'submission-detail');
      }
      const field = [
        [/accuracy.*(?:metres|meters|\(m\))/i, 'gps-accuracy'],
        [/consent to share/i, 'consent-answer'],
        [/confirm.*household records|accuracy confirmation/i, 'accuracy-confirm'],
        [/^state\s*\/\s*fct$/i, 'state'], [/^local government area$|^lga$/i, 'lga'],
        [/^ward$/i, 'ward'], [/^(latitude|longitude)(?:\b|$)/i, 'latitude'],
        [/^location source$/i, 'location-source'], [/^device capture time \(UTC\)$/i, 'location-time'],
        [/^(?:enumeration area(?: code)?|locality\s*\/\s*EA code)$/i, 'enumeration-area'],
        [/^(?:survey )?sponsor(?: name)?$/i, 'survey-sponsor'], [/^respondent(?: name)?$/i, 'survey-respondent'],
        [/^relationship to (?:household )?head$/i, 'member-relationship'],
        [/^date of birth$|^age \(if date of birth unknown\)$|^birth (?:year|month|day) \(/i, 'member-age'],
        [/^NIN \(11 digits; not authenticated\)$|^NIN tracking number$|^has a NIN or tracking number\?$/i, 'member-nin'],
        [/^bank account number \(10 digits\)$|^bank verification number \(11 digits\)$/i, 'member-banking'],
        [/^(?:total )?monthly (?:household )?income(?: \((?:NGN|optional)\))?$/i, 'monthly-income'],
        [/^main source of household income$/i, 'income-source'],
        [/^(?:affected by any major shock in the past 3 years\?|major shocks experienced)$/i, 'household-shock'],
        [/^health insurance(?: status| coverage)?$|^is anyone in the household covered by health insurance\?$/i, 'insurance-status'],
        [/^disability(?: status| type| severity)?$|^chronic (?:illness|condition)$|^has (?:any severe disability|a chronic illness)\?$|^uses a healthcare facility\?$/i, 'health-response'],
        [/^(?:number of (?:televisions?|generators?|livestock)(?: owned)?|asset type|does the household own any of the following assets\?)$/i, 'asset-response'],
        [/^(?:crops? (?:grown|cultivated)|does the household grow any crops\?)$/i, 'crops-grown']
      ].find(([pattern]) => pattern.test(s.field))?.[1];
      const fieldSections = {
        'gps-accuracy':'location', state:'location', lga:'location', ward:'location', latitude:'location',
        'location-source':'location', 'location-time':'location',
        'enumeration-area':'consent', 'consent-answer':'consent', 'survey-sponsor':'consent', 'survey-respondent':'consent',
        'member-relationship':'members', 'member-age':intake[1] === 'individual' ? 'identity' : 'members',
        'member-nin':'members', 'member-banking':'members',
        'monthly-income':'income', 'income-source':'income', 'household-shock':'income',
        'insurance-status':'vulnerability', 'health-response':'vulnerability', 'asset-response':'assets', 'crops-grown':'assets'
      };
      const defaultSection = fieldSections[field];
      const section = defaultSection || registrySection(s.section,s.sectionId);
      const key = section || (s.returnedIntake ? 'returned-intake' : s.intakeSection ? 'survey' : intake[2] === 'submission' ? 'draft' : intake[1] === 'individual' ? 'individual-intake' : 'intake');
      return context('register', key, field);
    }
    if (/^\/register\/(?:household|individual)\/[^/]+\/version-history$/.test(path)) return context('register', 'history');
    if (/\/change-request(?:\/|$)/.test(path)) {
      const key = /^\/change-request\/?$/.test(path) ? 'change-queue' :
        path.endsWith('/change-request') && path.startsWith('/register/') ? 'record-change-list' : 'change-detail';
      return context('register', key);
    }
    const published = path.match(/^\/register\/(household|individual)(?:\/([^/]+))?$/);
    if (published) {
      if (s.recordEditor) return context('register', 'change-create');
      if (published[2]) return context('register', published[1] + '-detail');
      return context('register', published[1] === 'household' ? 'households' : 'individuals');
    }
    if (path === '/offline') return context('register', offlineSections.get(s.section) || 'offline');
    if (path.startsWith('/configuration/')) return context('register', registryConfiguration(path.slice(15), s));
    if (path === '/incoming-messages') return context('register', 'incoming');
    if (path === '/outgoing-messages') return context('register', 'outgoing');
    if (path === '/myprofile') return context('register', 'state-missing');
    if (path === '/') {
      const section = registryDashboardSections.get(s.section);
      if (section) return context('register', section);
      const key =
        s.role === 'field' ? 'capture-dashboard' : s.role === 'officer' ? 'officer-dashboard' :
        ['level1', 'level2'].includes(s.role) ? 'review-dashboard' : 'overview';
      return context('register', key);
    }
  }

  function correctionSinceReturn(revision, history) {
    let returned = false;
    let corrected = false;
    for (const entry of history) {
      const event = entry.match(/^(.+?) · (Rejected|Corrected) · Revision (\d+)$/);
      if (!event || event[3] !== revision) continue;
      if (event[2] === 'Rejected') {
        returned = true;
        corrected = false;
      } else if (returned && event[1] === 'Programme Admin') {
        corrected = true;
      }
    }
    return corrected;
  }

  const reversalHelpRole = new Map([
    ['pbms-admin','programme-admin'],
    ['payment','payment'],
    ['finance','finance'],
    ['audit','audit'],
    ['ceo','ceo']
  ]);

  function pbms(s) {
    if (s.signIn || !/^\/pbms-ui(?:\/|$)/.test(s.path)) return;
    const route = s.hash.split('?')[0].slice(1) || 'programmes';
    const field = [
      [/^approval comment$/i, 'approval-comment'], [/^supporting document/i, 'supporting-doc'],
      [/^correction reason$/i, 'correction-reason'], [/^sponsor bank routing$/i, 'sponsor-routing'],
      [/^(?:workspace )?programme$/i, 'programme-selector'], [/^eligibility criteria/i, 'eligibility-editor']
    ].find(([pattern]) => pattern.test(s.field))?.[1];
    if (/^payment (status )?report$/i.test(s.dialog)) {
      const fields = s.paymentReportFields || [];
      if (s.paymentReportPending) return context('pbms','payment-report-pending');
      const role = reversalHelpRole.get(s.role);
      if (!s.paymentReportReversalAmountException && !s.paymentReportReversalMismatch && s.paymentReportPartial) {
        const key = 'payment-report-partial';
        return context('pbms',role ? key + '-' + role : key);
      }
      if (s.paymentReportReversalAmountException || s.paymentReportReversalMismatch || s.paymentReportReversed) {
        let key = 'payment-report-reversal';
        if (s.paymentReportReversalAmountException) key += '-amount-exception';
        else if (s.paymentReportReversalMismatch) key += '-mismatch';
        return context('pbms',role ? key + '-' + role : key);
      }
      if (fields.some(label => /disbursements reconciled/i.test(label))) return context('pbms','payment-report-envelope');
      if (fields.some(label => /sponsor bank dispatch status/i.test(label))) return context('pbms','payment-report-batch');
      return context('pbms', 'payment-report');
    }
    if (/^(?:new|edit) programme$/i.test(s.dialog)) return context('pbms', 'programme-editor', field);
    if (/^beneficiary workflow$/i.test(s.dialog)) {
      const progress = s.paymentSubmitted || route === 'payments' || s.explicitStage === 'Payments';
      const key = s.explicitStage === 'Verification queue' ? 'verification' :
        s.section === 'Payment envelopes' ? 'payment-envelopes' :
        s.section === 'Payment batches' ? 'payment-batches' : progress ? 'payment-progress' : 'lists';
      return context('pbms', key);
    }
    if (/confirm approval/i.test(s.dialog)) return context('pbms', 'approvals');
    if (/^confirm payment submission$/i.test(s.dialog)) return context('pbms','payment-confirm');
    if (/^disbursement approval list$/i.test(s.dialog)) {
      let key = 'flow-open';
      const overview = !['Approval','Beneficiaries','Verification history','Payments'].includes(s.section);
      if (s.section === 'Verification history') key = 'flow-history';
      else if (s.exportList && s.section === 'Beneficiaries') key = 'flow-export';
      else if (s.section === 'Payments' || field === 'sponsor-routing' || (overview && s.listStatus==='Fully verified')) {
        if (s.paymentSubmitted) key = 'flow-payment-submitted';
        else if (s.canRouteList) key = 'flow-routing';
        else if (s.canPayList) key = 'flow-payment';
        else if (s.role === 'payment' && s.paymentRoutingMissing) key = 'flow-payment-wait-route';
        else if (s.exportList && overview) key = 'flow-export';
        else key = 'flow-payment-read';
      }
      else if (s.correctList && (s.section === 'Beneficiaries' || field === 'correction-reason')) key = 'flow-correct';
      else if (s.listStatus === 'Returned for correction') {
        if (s.canSubmitList) key = s.correctionRecorded ? 'flow-resubmit' : 'flow-resubmit-wait';
        else if (s.correctList) key = s.correctionRecorded ? 'flow-correction-saved' : 'flow-correct';
        else key = 'flow-returned';
      }
      else if (s.canSubmitList) key = 'flow-submit';
      else {
        const stage = {'Awaiting Finance': 'finance', 'Awaiting Audit': 'audit', 'Awaiting CEO': 'ceo'}[s.listStatus];
        if (stage) key = s.canDecideList ? stage : 'decision-visible';
      }
      const contextualField = field === 'approval-comment' && s.canSubmitList ? 'submission-comment' : field;
      return context('pbms', key, contextualField);
    }
    if (route === 'programme-flow') {
      if (/^(?:registration|disbursement) (?:start|end)$/i.test(s.field)) {
        return context('pbms','flow-enrollment','cycle-window-date');
      }
      if (/^schedule date$/i.test(s.field)) return context('pbms','flow-disbursement','cycle-schedule-date');
      const variants = [
        [/^monthly enrol(?:l)?ment cycles$/i, 'flow-enrollment'],
        [/^monthly disbursement cycles$/i, 'flow-disbursement'],
        [/master and approval configuration|create programme/i, 'flow-setup'],
        [/enrol(?:l)?ment and disbursement lists/i, 'flow-lists'],
        [/programme staff access/i, 'flow-access']
      ];
      const key = variants.find(([pattern]) => pattern.test(s.section || s.flowHeading))?.[1];
      return context('pbms', key || 'flow', field);
    }
    const known = ['programmes','programme-detail','enrollment','disbursement','lists','verification','approvals',
      'payments','eligibility','entitlements','benefits','programme-benefits','enrollment-workflow','disbursement-workflow',
      'households','farmers','students','priority','agencies','warehouses','states','lgas','agency-benefits','warehouse-benefits'];
    if (route === 'programme-analytics') return context('pbms', 'analytics', field);
    if (known.includes(route)) return context('pbms', route, field);
  }

  function resolve(input) {
    const s = {section: '', field: '', path: '/', dialog: '', hash: '', ...input};
    const staffSignIn = s.service === 'keycloak' && s.path.startsWith('/realms/staff/') ||
      s.service === 'pbms' && /^\/pbms-ui(?:\/|$)/.test(s.path);
    if (s.signIn && staffSignIn && /^email$/i.test(s.field)) {
      return context('platform','sign-in','sign-in-email');
    }
    if (s.service === 'register' && !s.signIn) return registry(s);
    if (s.service === 'pbms') return pbms(s);
    if (['g2p','nigeriag2p'].includes(s.service) && s.role === 'verifier') {
      const field = new Map([
        ['The household details are complete.','case-completeness'],
        ['The correction reason has been addressed.','case-correction'],
        ['I understand this approves registration only.','case-registration-only']
      ]).get(s.field);
      if (field) return context('review','case-checks',field);
      if (s.section === 'Household members') return context('review','case-members');
      if (s.section === 'Confirm the current household details.') return context('review','case-checks');
    }
    if (s.signIn) return;
    if (s.service === 'awe' && /^\/requests\/?$/.test(s.path)) return context('awe', 'requests');
    if (s.service === 'awe' && /^\/requests\//.test(s.path)) return context('awe', 'detail');
    if (s.service === 'partner-management' && /^\/partners\/?$/.test(s.path)) return context('partner-management','directory');
    if (s.service === 'partner-management' && /^\/partners\/[^/]+\/?$/.test(s.path)) return context('partner-management','partner-detail');
    if (s.service === 'beneficiary' && /^\/selfservice\/(?:[a-z]{2}\/)?programs\/?$/i.test(s.path)) return context('beneficiary','programmes');
    if (s.service === 'beneficiary' && /^\/selfservice\/(?:[a-z]{2}\/)?registries\/?$/i.test(s.path)) return context('beneficiary','registries');
    if (s.service === 'staff-portal' && s.path === '/' && !s.signIn) return context('staff-portal', 'services');
    if (s.path === '/registration/knowledge') return context('knowledge', 'browse');
  }

  return {resolve, correctionSinceReturn};
});
