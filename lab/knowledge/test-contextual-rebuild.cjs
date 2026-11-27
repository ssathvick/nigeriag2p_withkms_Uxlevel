const assert = require('node:assert/strict');
const {resolve, correctionSinceReturn} = require('./contextual');
const articles = require('../knowledge-seed.json').articles;
const catalog = require('./contextual-catalog.json');
const typed = new Map(articles.filter(article => article.context_key).map(article => [article.context_key, article]));

for (const article of catalog) {
  const key = 'context-' + article.group + '-' + article.key;
  const entry = typed.get(key);
  assert(entry?.provisional, key);
  assert.equal(entry.help_level, article.help_level, key);
  assert.equal(entry.title, article.title, key);
  assert(entry.purpose && entry.source_note, key);
}
assert.equal(typed.size,catalog.length);
assert.equal(new Set(catalog.map(entry => entry.group === 'imports' ? 'register' : entry.group)).size,18);

const check = (input, slug, field) => {
  const actual = resolve(input);
  assert.equal(actual?.slug, 'context-' + slug, JSON.stringify(input));
  assert(typed.has(actual.slug));
  if (field) {
    assert.equal(actual.fieldSlug, 'context-' + field, JSON.stringify(input));
    assert.equal(typed.get(actual.fieldSlug)?.help_level,'field');
  }
};
const registry = (path, key, options = {}, field) =>
  check({service:'register',path:'/en' + path,...options},'register-' + key,field && 'register-' + field);
registry('','overview',{role:'admin'});
registry('','capture-dashboard',{role:'field'});
registry('','officer-dashboard',{role:'officer'});
registry('','review-dashboard',{role:'level2'});
registry('/register/household','households');
registry('/register/individual','individuals');
registry('/register/household/example','household-detail');
registry('/register/individual/example','individual-detail');
registry('/register/individual/example/version-history','history');
registry('/register/individual/example','change-create',{recordEditor:true});
registry('/intake-form/household','submission-queues');
registry('/intake-form/household/new/example','intake');
registry('/intake-form/individual/new/example','individual-intake');
registry('/intake-form/household/new/example','location',{section:'Household location',field:'Location accuracy (metres)'},'gps-accuracy');
registry('/intake-form/household/new/example','location',{section:'Nigeria administrative location',sectionId:'hh_survey_consent'});
registry('/intake-form/household/new/example','consent',{section:'Survey Consent & Enumeration',field:'Consent to share data'},'consent-answer');
registry('/intake-form/household/new/example','members',{section:'Household Member Details'});
registry('/intake-form/household/new/example','vulnerability',{section:'Health Insurance Coverage'});
registry('/intake-form/household/new/example','income',{section:'Household income and coping'});
registry('/intake-form/household/new/example','assets',{section:'Crops Grown'});
registry('/intake-form/household/new/example','conditions',{section:'Household Living & Dwelling Characteristics'});
registry('/intake-form/household/submission/example','draft',{intakeEditor:true});
registry('/intake-form/household/submission/example','returned-intake',{intakeEditor:true,returnedIntake:true});
registry('/intake-form/household/submission/example','location',
  {intakeEditor:true,returnedIntake:true,field:'Location source'},'location-source');
registry('/intake-form/household/new/example','members',
  {field:'Relationship to household head',dialog:'Add Household Member'},'member-relationship');
registry('/intake-form/household/submission/example','submission-detail');
registry('/tasks/intake-form','intake-queue');
for (const [role, guide] of [['level1','review-l1'], ['level2','review-l2']]) {
  registry('/tasks/intake-form',guide,{role,assignedIntakeTask:true});
  registry('/tasks/intake-form','intake-queue',{role,assignedIntakeTask:false});
  registry('/intake-form/household/submission/example',guide,{role,canReview:true});
  registry('/intake-form/household/submission/example','submission-detail',{role,canReview:false});
}
registry('/intake-form/household/submission/example','returned-intake',{
  role:'field', intakeEditor:true, returnedIntake:true, intakeSection:true, section:'Review feedback'
});
for (const role of ['all','field','level1','level2','officer','admin']) {
  registry('/','submission-queues',{role,section:'Form submissions'});
}
registry('/tasks/intake-form/household/example','review-l1',{role:'level1',canReview:true,field:'Message'},'decision-note');
registry('/tasks/intake-form/household/example','review-l2',{role:'level2',canReview:true});
registry('/tasks/intake-form/household/example','review-intake',{role:'level2',canReview:false});
registry('/tasks/intake-form/household/example','duplicates',{section:'Potential duplicates'});
registry('/tasks/intake-form/household/example','duplicates-intake',{duplicateView:'duplicates-intake',role:'level1',canReview:true});
registry('/intake-form/household/submission/example','duplicates-register',{duplicateView:'duplicates-register',role:'admin'});
registry('/tasks/change-request','change-task-queue');
registry('/tasks/change-request/example','change-detail');
registry('/change-request','change-queue');
registry('/configuration/registry/users','staff');
registry('/configuration/data-policies/new','policy-create');
registry('/configuration/ingest-configurations/semantic-patterns','ingest-patterns');
registry('/offline','offline');
registry('/incoming-messages','incoming');
registry('/outgoing-messages','outgoing');


for (const [path, key] of [
  ['/configuration/awe-policy-config', 'approval-policies'],
  ['/configuration/data-models', 'data-models'],
  ['/configuration/data-policies', 'data-policies'],
  ['/configuration/intake-forms', 'form-definitions'],
  ['/configuration/intake-forms/form', 'form-tabs'],
  ['/configuration/intake-forms/form/tabs/tab', 'form-sections'],
  ['/configuration/registers', 'register-definitions'],
  ['/configuration/registers/example', 'register-structure'],
  ['/configuration/registers/example/sections/section', 'register-section'],
  ['/configuration/registers/example/tabs/tab', 'register-tab'],
  ['/configuration/registers/example/scores/score', 'register-score'],
  ['/configuration/registry/details', 'registry-details'],
  ['/configuration/registry/languages', 'registry-languages'],
  ['/configuration/registry/themes', 'registry-themes'],
  ['/configuration/registry/themes/create', 'theme-create'],
  ['/configuration/ingest-configurations/templates', 'ingest-templates'],
  ['/configuration/ingest-configurations/key-paths', 'ingest-paths'],
  ['/configuration/ingest-configurations/manage-subscription', 'ingest-subscriptions'],
  ['/configuration/outgest-configurations/templates', 'outgoing-templates'],
  ['/configuration/outgest-configurations/topics', 'outgoing-topics'],
  ['/incoming-messages/change-request/example', 'change-detail'],
  ['/register/household/example/change-request', 'record-change-list'],
  ['/register/household/example/change-request/change', 'change-detail'],
  ['/change-request/example', 'change-detail'],
  ['/myprofile', 'state-missing'],
]) registry(path, key);

for (const [heading, key] of [
  ['Register your household', 'registration-start'], ['Master Registry', 'published-registers'],
  ['Form submissions', 'submission-queues'], ['My tasks', 'review-dashboard'],
  ['Change requests', 'change-queue'], ['From capture to master record', 'journey'],
]) registry('/', key, {section:heading, role:'admin'});
registry('/offline', 'offline-device', {section:'Prepare your device'});
registry('/offline', 'offline-delivery', {section:'Reconnect and confirm delivery'});
registry('/configuration/registry/users', 'staff-onboarding', {section:'Onboard a staff member'});
registry('/configuration/registry/users', 'staff-responsibilities', {section:'Independent responsibilities'});
registry('/configuration/data-policies/new', 'policy-filters', {section:'Filter rules'});
registry('/configuration/data-policies', 'configuration-navigation', {configurationNav:true});
for (const [state, key] of [
  ['Access restricted','state-restricted'], ['Page not found','state-missing'],
  ['We could not load this page','state-error'],
]) registry('/register/household/example', key, {registryPageState:state, recordEditor:true});
registry('/register/household-list','state-missing',{registryPageState:'Page not found'});
registry('/tasks/intake-form/household/example','review-l1',
  {section:'Review decision', duplicateView:'duplicates-intake', role:'level1',canReview:true,field:'Message'}, 'decision-note');
registry('/tasks/intake-form/household/example','duplicates-register',{duplicateView:'duplicates-register',section:'Match #1'});

const imports = (key, options, field) =>
  check({service:'register',path:'/en/data-imports',...options},'imports-' + key,field && 'imports-' + field);
imports('operator',{role:'field'});
imports('approver',{role:'level1'});
imports('admin',{role:'admin'});
imports('denied',{role:'level2',denied:true});
imports('source',{role:'admin',tab:'Sources and mappings'});
imports('transfers',{section:'Transfer history',role:'admin'});
imports('access',{role:'admin',tab:'Access'});
imports('start',{tab:'New import',field:'Data source'},'source-choice');
imports('fetch',{role:'field',tab:'New import',importConnected:true,field:'Data source'},'source-choice');
imports('fetch-error',{role:'field',tab:'New import',importConnected:true,importFetchError:true});
imports('choose-fetch',{role:'field',tab:'New import',importConnected:true,importChooseFetch:true});
imports('fetch-error',{role:'field',batch:true,importStatus:'Ingested by Registry',importFetchError:true});
imports('expected-columns',{role:'field',tab:'New import',importConnected:true,section:'Expected columns'});
imports('prepare',{role:'field',tab:'New import',batch:true,importStatus:'Draft',importConnected:true});
imports('shared-fetch',{role:'field',batch:true,importStatus:'Draft',importSharedFetch:true});
imports('receipt',{role:'field',batch:true,importStatus:'Ingested by Registry',importSharedFetch:true});
imports('receipt-after-job-failure',{role:'field',batch:true,importStatus:'Ingested by Registry',importReceivedWithError:true});
imports('receipt-after-job-failure',{role:'admin',batch:true,section:'Registry receipt',importStatus:'Ingested by Registry',importReceivedWithError:true,importFetchError:true});
imports('receipt-log-missing',{role:'field',batch:true,importStatus:'Ingested by Registry',importSavedWithoutLog:true,importReceivedWithError:true});
imports('receipt-log-missing',{role:'admin',batch:true,section:'Registry receipt',importStatus:'Partially ingested',importSavedWithoutLog:true});
imports('receipt-log-restored',{role:'admin',batch:true,section:'Registry receipt',importStatus:'Ingested by Registry',importReceiptLogRestored:true});
imports('receipt-log-missing',{role:'field',batch:true,section:'Registry receipt',importStatus:'Ingested by Registry',importSavedWithoutLog:true,importReceiptLogRestored:true});
imports('failed',{role:'level1',batch:true,importStatus:'Ingestion needs attention'});
imports('review',{batch:true,return:true,field:'Reason for returning this batch'},'return-note');
for (const [status,key] of [
  ['Draft','prepare'], ['Awaiting approval','awaiting-review'], ['Returned for correction','returned-read'],
  ['Approved','approved-read'], ['Ready to retry','retry-read'], ['Submitting to Registry','submitting'],
  ['Submission unconfirmed','unconfirmed'], ['Queued at Registry','queued'], ['Ingested by Registry','receipt'],
  ['Partially ingested','partial'], ['Ingestion needs attention','failed'],
]) imports(key,{batch:true,importStatus:status});
imports('ready',{batch:true,importStatus:'Approved',transfer:true});
imports('transfer-conflict',{batch:true,importStatus:'Approved',transfer:true,importTransferConflict:true});
imports('retry',{batch:true,importStatus:'Ready to retry',retry:true});
imports('correct',{batch:true,importStatus:'Returned for correction',correct:true});
imports('partial',{batch:true,importStatus:'Partially ingested',section:'Registry receipt'});
for (const [role,key] of [['field','partial-field'], ['level1','partial-review'], ['admin','partial-admin']]) {
  imports(key,{role,batch:true,importStatus:'Partially ingested'});
  imports(key,{role,batch:true,importStatus:'Partially ingested',section:'Registry receipt',importFetchError:true});
}
imports('denied',{role:'level2',denied:true,batch:true,importStatus:'Partially ingested',section:'Registry receipt'});
for (const [role,suffix] of [['all',''], ['field','-field'], ['level1','-review'], ['admin','-admin']]) {
  imports('duplicate-receipt'+suffix,{role,batch:true,importStatus:'Awaiting approval',section:'Review decision',importRowConflict:true});
}
imports('activity',{role:'admin',batch:true,importStatus:'Approved',section:'Activity',importRowConflict:true});
imports('reconcile',{batch:true,importStatus:'Partially ingested',section:'Reconcile records',field:'Issues and exclusions only'},'issues-filter');
imports('source',{tab:'Sources and mappings',field:'Spreadsheet column'},'mapping-columns');
imports('source',{tab:'Sources and mappings',field:'Field for duplicate checks'},'mapping-duplicate-key');
imports('test-mapping',{tab:'Sources and mappings',section:'Test mapping with sample values'});
imports('expected-columns',{tab:'New import',section:'Expected columns'});
imports('reconcile',{batch:true,section:'Reconcile records',field:'Exclude this row from the transfer'},'exclude-row');

const pbms = (key, options = {}, field) =>
  check({service:'pbms',path:'/pbms-ui/',...options},'pbms-' + key,field && 'pbms-' + field);
for (const route of ['programmes','programme-detail','programmes','enrollment','disbursement','lists','verification',
  'approvals','payments','eligibility','entitlements','benefits','programme-benefits','enrollment-workflow','disbursement-workflow',
  'households','farmers','students','priority','agencies','warehouses','states','lgas','agency-benefits','warehouse-benefits'])
  pbms(route,{hash:'#' + route + '?program_id=1'});
pbms('flow-enrollment',{hash:'#programme-flow',section:'Monthly enrolment cycles'});
pbms('flow-disbursement',{hash:'#programme-flow',section:'Monthly disbursement cycles'});
pbms('flow-setup',{hash:'#programme-flow',section:'Programme master and approval configuration',field:'Eligibility criteria'},'eligibility-editor');
pbms('flow-lists',{hash:'#programme-flow',section:'Enrolment and disbursement lists'});
pbms('flow-access',{hash:'#programme-flow',section:'Programme staff access'});
const detail = {dialog:'Disbursement approval list'};
pbms('finance',{...detail,listStatus:'Awaiting Finance',canDecideList:true,field:'Approval comment'},'approval-comment');
pbms('audit',{...detail,listStatus:'Awaiting Audit',canDecideList:true});
pbms('ceo',{...detail,listStatus:'Awaiting CEO',canDecideList:true});
pbms('decision-visible',{...detail,listStatus:'Awaiting CEO',canDecideList:false});
pbms('flow-submit',{...detail,canSubmitList:true});
pbms('flow-correct',{...detail,listStatus:'Returned for correction',correctList:true});
const returned = {...detail,listStatus:'Returned for correction'};
pbms('flow-correct',{...returned,correctList:true,section:'Approval'});
pbms('flow-correction-saved',{...returned,correctList:true,correctionRecorded:true});
pbms('flow-correct',{...returned,correctList:true,correctionRecorded:true,section:'Beneficiaries'});
pbms('flow-returned',returned);
pbms('flow-resubmit-wait',{...returned,canSubmitList:true,field:'Approval comment'},'submission-comment');
pbms('flow-resubmit',{...returned,canSubmitList:true,correctionRecorded:true,section:'Approval'});
pbms('flow-submit',{...detail,canSubmitList:true,field:'Approval comment'},'submission-comment');
const correction = 'Programme Admin · Corrected · Revision 2';
const rejection = 'Audit · Rejected · Revision 2';
assert.equal(correctionSinceReturn('2',[correction,rejection]),false);
assert.equal(correctionSinceReturn('2',[rejection,correction]),true);
assert.equal(correctionSinceReturn('3',[rejection,correction]),false);
assert.equal(correctionSinceReturn('2',[rejection,correction,rejection]),false);
const verified = {...detail,listStatus:'Fully verified'};
pbms('flow-export',{...verified,exportList:true});
pbms('flow-payment',{...verified,canPayList:true});
pbms('flow-payment-wait-route',{...verified,section:'Example disbursement list',role:'payment',paymentRoutingMissing:true});
pbms('flow-payment',{...verified,section:'Payments',role:'payment',canPayList:true});
pbms('flow-payment-read',{...detail,section:'Payments',role:'audit'});
pbms('flow-routing',{...detail,section:'Payments',field:'Sponsor bank routing',canRouteList:true},'sponsor-routing');
pbms('flow-routing',{...verified,exportList:true,canRouteList:true});
pbms('flow-payment-wait-route',{...verified,role:'payment',paymentRoutingMissing:true});
pbms('payment-confirm',{dialog:'Confirm payment submission'});
for (const field of ['Registration start','Registration end','Disbursement start','Disbursement end']) {
  check({service:'pbms',path:'/pbms-ui/',hash:'#programme-flow',field},'pbms-flow-enrollment','pbms-cycle-window-date');
}
check({service:'pbms',path:'/pbms-ui/',hash:'#programme-flow',field:'Schedule date'},
  'pbms-flow-disbursement','pbms-cycle-schedule-date');
pbms('flow-payment-submitted',{...verified,role:'payment',paymentSubmitted:true});
pbms('flow-payment-submitted',{...verified,role:'audit',section:'Payments',paymentSubmitted:true});
pbms('flow-export',{...verified,exportList:true,section:'Beneficiaries',paymentSubmitted:true});
pbms('payment-progress',{dialog:'Beneficiary workflow',paymentSubmitted:true});
pbms('payment-envelopes',{dialog:'Beneficiary workflow',section:'Payment envelopes',explicitStage:'Payments'});
pbms('payment-batches',{dialog:'Beneficiary workflow',section:'Payment batches',explicitStage:'Payments'});
pbms('payment-report-envelope',{dialog:'Payment report',paymentReportFields:['Number Of Disbursements Reconciled']});
pbms('payment-report-reversal',{dialog:'Payment report',paymentReportFields:['Number Of Disbursements Reversed'],
  paymentReportReversed:true});
const reversalMismatch = {dialog:'Payment report',paymentReportReversed:true,paymentReportReversalMismatch:true};
const amountException = {...reversalMismatch,paymentReportReversalAmountException:true};
const partial = {dialog:'Payment report',paymentReportPartial:true};
pbms('payment-report-partial',partial);
pbms('payment-report-reversal-mismatch',{...partial,...reversalMismatch});
pbms('payment-report-reversal-amount-exception',{...partial,...amountException});
pbms('payment-report-pending',{...partial,paymentReportPending:true});
pbms('payment-report-reversal-mismatch',reversalMismatch);
pbms('payment-report-reversal-amount-exception',amountException);
for (const [role,key] of Object.entries({'pbms-admin':'programme-admin',payment:'payment',finance:'finance',audit:'audit',ceo:'ceo'})) {
  pbms('payment-report-reversal-'+key,{dialog:'Payment report',paymentReportFields:['Number Of Disbursements Reversed'],
    paymentReportReversed:true,role});
  pbms('payment-report-reversal-mismatch-'+key,{...reversalMismatch,role});
  pbms('payment-report-reversal-amount-exception-'+key,{...amountException,role});
  pbms('payment-report-partial-'+key,{...partial,role});
}
pbms('payment-report-batch',{dialog:'Payment report',paymentReportFields:['Sponsor Bank Dispatch Status']});
pbms('payment-report-pending',{dialog:'Payment report',paymentReportPending:true});
pbms('payment-report-pending',{...reversalMismatch,paymentReportPending:true});
pbms('payment-report-pending',{...amountException,paymentReportPending:true});
pbms('flow-history',{...detail,section:'Verification history'});
pbms('payment-report',{dialog:'Payment status report'});
assert.equal(resolve({service:'pbms',path:'/pbms-ui/',signIn:true}),undefined);
for (const [service,path] of [['keycloak','/realms/staff/protocol/openid-connect/auth'],['pbms','/pbms-ui/']]) {
  check({service,path,signIn:true,field:'Email'},'platform-sign-in','platform-sign-in-email');
}
assert.equal(resolve({service:'keycloak',path:'/realms/beneficiary/protocol/openid-connect/auth',signIn:true,field:'Email'}),undefined);
check({service:'g2p',path:'/registration/workspace',role:'verifier',section:'Household members'},'review-case-members');
check({service:'g2p',path:'/registration/workspace',role:'verifier',field:'The correction reason has been addressed.'},
  'review-case-checks','review-case-correction');
check({service:'partner-management',path:'/partners'},'partner-management-directory');
check({service:'partner-management',path:'/partners/example'},'partner-management-partner-detail');
check({service:'beneficiary',path:'/selfservice/en/programs'},'beneficiary-programmes');
check({service:'beneficiary',path:'/selfservice/en/registries'},'beneficiary-registries');
assert.equal(resolve({service:'beneficiary',path:'/selfservice/en/programs/apply/example'}),undefined);
console.log('Catalog covers',typed.size,'authored guides across 18 services. Priority screen, role, state and field mapping cases passed.');

// Verify the V0.2 household field hints and the parent screen for each.
const intakeHints = [
  ['Community / area', 'consent'], ['Survey serial number','consent'], ['Household address','consent'],
  ['Community (optional)','location'], ['Reported location / address','location'], ['Altitude (metres)','location'],
];
for (const [field, parent] of intakeHints) {
  const input = {service:'register', path:'/en/intake-form/household/new/example', role:'field', field};
  const guide = resolve(input);
  assert.equal(guide.slug, 'context-register-' + parent);
  assert.equal(guide.fieldHelp.label, field);
  assert.ok(guide.fieldHelp.description.length > 10);
  assert.equal(resolve({...input, path:'/en/intake-form/individual/new/example'}).fieldHelp, undefined);
}
for (const [role, guide] of Object.entries({field:'registration-start',officer:'officer-dashboard',level1:'review-dashboard',level2:'review-dashboard'})) {
  registry('',guide,{section:'Register your household',role});
}
registry('/register/household/example','history',{section:'Record version history'});
registry('/register/household/example','record-change-list',{section:'Change requests'});
