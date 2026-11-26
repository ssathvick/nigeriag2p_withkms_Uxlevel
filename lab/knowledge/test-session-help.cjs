// Run with the PBMS Playwright development dependency. All browser requests
// are fulfilled locally using the checked-in seed and synthetic identities.
const assert = require('node:assert/strict');
const path = require('node:path');
const { chromium } = require(require.resolve('playwright', {paths:[path.join(__dirname,'../pbms-react'),__dirname]}));
const seed = require('../knowledge-seed.json');

async function run() {
  const browser = await chromium.launch({executablePath:process.env.KMS_TEST_BROWSER || undefined});
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror',error => errors.push(error.message));
    let role = 'level1';
    let releaseOldRequest, oldRequestStarted;
    const started = new Promise(resolve => { oldRequestStarted = resolve; });
    let delayNext = false;
    await page.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.pathname === '/api/me') {
        const scope = role;
        if (delayNext) {
          delayNext = false;
          await new Promise(resolve => { releaseOldRequest = resolve; oldRequestStarted(); });
        }
        return route.fulfill({json:{registry_scope:scope}});
      }
      if (url.pathname === '/iqs-brand/knowledge') {
        return route.fulfill({json:{...seed, articles:seed.articles.map((a,i) => ({...a,id:i+1,version:1}))}});
      }
      if (route.request().isNavigationRequest()) {
        return route.fulfill({contentType:'text/html',body:'<main><h1>Approvals</h1><span title="open">Open</span></main>'});
      }
      return route.abort();
    });
    await page.goto('https://g2p-register.wverve.in/en/tasks/intake-form');
    for (const name of ['context.js','contextual.js','contextual-help.js']) {
      await page.addScriptTag({path:path.join(__dirname,name)});
    }
    const launcher = page.locator('#ng-km-launcher');
    const note = page.locator('#ng-km-context');
    const heading = page.locator('#ng-km-panel h3');
    const check = async (name,key) => {
      const title = seed.articles.find(a => a.slug === 'context-register-' + key).title;
      await page.waitForFunction(([label,title]) =>
        document.querySelector('#ng-km-context').textContent.includes(label) &&
        document.querySelector('#ng-km-panel h3')?.textContent === title,[name,title]);
      assert((await note.textContent()).includes(name));
      assert.equal(await heading.first().textContent(),title);
    };
    await launcher.click();
    await check('First Reviewer','review-l1');
    // Log out and back in without a full navigation or different URL.
    await page.evaluate(() => document.querySelector('main').innerHTML = '<input type="password">');
    await page.waitForFunction(() => !document.querySelector('#ng-km-context').textContent.includes('First Reviewer'));
    role = 'level2';
    await page.evaluate(() => document.querySelector('main').innerHTML = '<h1>Approvals</h1><span title="open">Open</span>');
    await check('Second Reviewer','review-l2');
    // A late reply from a previous route must not overwrite the new identity.
    delayNext = true;
    await page.evaluate(() => { location.hash = 'before-switch'; });
    await started;
    role = 'level1';
    await page.evaluate(() => { location.hash = 'after-switch'; });
    await check('First Reviewer','review-l1');
    assert.equal(typeof releaseOldRequest,'function');
    const finished = page.waitForResponse(res => res.url().endsWith('/api/me'));
    releaseOldRequest();
    await finished;
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.locator('#ng-km-panel .ng-km-follow').evaluate(button => button.click());
    await check('First Reviewer','review-l1');
    await launcher.click();
    await launcher.click();
    await check('First Reviewer','review-l1');
    assert.deepEqual(errors,[]);
    console.log('Help followed a same-page sign-out, sign-in and a role change with an older identity request in flight.');
  } finally {
    await browser.close();
  }
}
run().catch(error => { console.error(error); process.exitCode = 1; });
