// Disposable offline fixture. Never opens Google Flow or authenticates an account.
const { chromium } = require('../.tools/browser/node_modules/playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'film-credit-smoke-'));
  const env = { ...process.env, DIRECTOR_DATA: directory, DIRECTOR_NO_SEED: '1' };
  async function python(script) {
    return new Promise((resolve, reject) => {
      const child = spawn('.venv/bin/python', ['-c', script], { env, stdio: ['ignore', 'pipe', 'pipe'] });
      let stdout = '', stderr = '';
      child.stdout.on('data', x => stdout += x); child.stderr.on('data', x => stderr += x);
      child.on('error', reject);
      child.on('exit', code => code === 0 ? resolve(JSON.parse(stdout)) : reject(new Error(stderr)));
    });
  }
  let server, browser, log;
  try {
    const fixture = await python(`import json, os
from tests.test_film import FilmTests
from studio.store import Store
from studio.film import FilmService
FilmTests.setUpClass()
try:
    h=FilmTests(); h.store=Store(os.environ['DIRECTOR_DATA']); h.service=FilmService(h.store)
    h.p,h.scene,h.claim,h.board=h.fixture()
    p=h.package()
    print(json.dumps({'project_id':h.p,'package_id':p['id'],'package_hash':p['hash']}))
finally:
    FilmTests.tearDownClass()
`);
    const probe = require('node:net').createServer();
    await new Promise(resolve => probe.listen(0, '127.0.0.1', resolve));
    const port = probe.address().port;
    await new Promise(resolve => probe.close(resolve));
    const base = `http://127.0.0.1:${port}`;
    log = fs.openSync('.tools/film-browser-server.log', 'w');
    server = spawn('.venv/bin/python', ['-m', 'uvicorn', 'studio.app:app', '--host', '127.0.0.1', '--port', String(port)], { env, stdio: ['ignore', log, log] });
    let ready = false;
    for (let i=0;i<80;i++) {
      if (server.exitCode !== null) throw new Error('Fixture server exited; see .tools/film-browser-server.log');
      try { if ((await fetch(`${base}/api/session`)).ok) { ready = true; break; } } catch {}
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    assert(ready, 'Temporary film server did not start');
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, timezoneId: 'UTC' });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    page.setDefaultTimeout(5000);
    await page.goto(base);
    const panel = page.getByRole('region', { name: 'Film packages and credit limits', exact: true });
    try {
      await panel.getByRole('heading', { name: 'Film packages and credit limits', exact: true }).waitFor();
    } catch (error) {
      console.error('Film UI startup errors:', errors);
      await page.screenshot({ path: '.tools/film-startup-failure.png', fullPage: true });
      throw error;
    }
    const initialState=await (await fetch(`${base}/api/projects/${fixture.project_id}/film`)).json();
    assert.equal(initialState.packages[0].id,fixture.package_id,'Rendered project must retain the prepared package identity');
    const pack = panel.getByRole('article', { name: `Film package ${fixture.package_id}`, exact: true });
    try {
      assert.equal(await pack.getByLabel('Exact approved prompt', { exact: true }).inputValue(), 'Exact reviewed prompt');
    } catch (error) {
      await page.screenshot({ path: '.tools/film-failure.png', fullPage: true });
      console.error(await panel.innerText(), errors);
      console.error(await panel.locator('article').evaluateAll(elements => elements.map(e => e.outerHTML.slice(0, 500))));
      throw error;
    }
    assert(await pack.getByText('Current inputs', { exact: true }).isVisible());
    assert(await pack.locator('img').isVisible());
    await panel.getByLabel('Project credit cap', { exact: true }).fill('75');
    await panel.getByLabel('Budget decision note', { exact: true }).fill('Offline browser fixture only');
    await panel.getByLabel('Confirm this project credit cap', { exact: true }).check();
    await panel.getByRole('button', { name: 'Save credit cap', exact: true }).click();
    await panel.getByText('Project cap: 75 credits', { exact: true }).waitFor();
    await pack.getByLabel('Package review note', { exact: true }).fill('Fixture exact package checked');
    await pack.getByLabel('I reviewed this exact prompt, references and settings', { exact: true }).check();
    await pack.getByRole('button', { name: 'Approve package', exact: true }).click();
    await pack.getByText('Package review: approved', { exact: false }).waitFor();
    await pack.getByLabel('Cumulative attempt ceiling', { exact: true }).fill('3');
    await pack.getByLabel('Cumulative credit ceiling', { exact: true }).fill('15');
    await pack.getByLabel('Allowance expiry', { exact: true }).fill(new Date(Date.now()+3600000).toISOString().slice(0,16));
    await pack.getByLabel('Allowance decision note', { exact: true }).fill('No real provider submission');
    await pack.getByLabel('Authorize these exact references and settings within these limits', { exact: true }).check();
    await pack.getByRole('button', { name: 'Approve spending allowance', exact: true }).click();
    await pack.getByText(/Saved ceiling: 3 attempts/).waitFor();
    await python(`import json, os
from studio.store import Store
from studio.film import FilmService
s=Store(os.environ['DIRECTOR_DATA']); f=FilmService(s)
with s.db() as db:
    claim=dict(db.execute("SELECT * FROM tasks WHERE project_id=? AND stage='flow' AND status='claimed'", (${JSON.stringify(fixture.project_id)},)).fetchone())
a=f.reserve_attempt(${JSON.stringify(fixture.package_id)},claim['id'],claim['token'])
f.record_result(a['id'],{'status':'unknown','evidence':'Simulated interrupted browser fixture; no external action'},claim['id'],claim['token'])
print(json.dumps({'attempt_id':a['id']}))
`);
    await page.getByRole('button', { name: 'Refresh project', exact: true }).click();
    await panel.getByText('Committed: 5 credits · Remaining: 70', { exact: true }).waitFor();
    await page.reload();
    await panel.getByText('Committed: 5 credits · Remaining: 70', { exact: true }).waitFor();
    await panel.getByRole('heading', { name: 'Attempt history', exact: true }).waitFor();
    assert(await panel.getByText('unknown', { exact: true }).first().isVisible());
    assert.equal(await page.getByRole('button', { name: /^Generate/ }).count(), 0);
    const state = await (await fetch(`${base}/api/projects/${fixture.project_id}/film`)).json();
    assert.equal(state.attempts[0].status, 'unknown');
    assert.equal(state.attempts[0].local_download_verified, false);
    assert.equal(state.budget.committed_credits, 5);
    assert.equal(state.decisions.length, 1);
    assert.equal(state.allowances.length, 1);
    assert(Object.values(state.automation).every(v => v === false));
    await page.screenshot({ path: '.tools/film-desktop.png', fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Film panel mobile overflow');
    await page.screenshot({ path: '.tools/film-mobile.png', fullPage: true });
    assert.deepEqual(errors, []);
    console.log('PASS: exact film package/ref review, separate credit cap and allowance, reserved unknown result after reload, no live Generate, desktop/mobile, no page errors.');
  } finally {
    if (browser) await browser.close();
    if (server && server.exitCode === null) { server.kill('SIGTERM'); await new Promise(resolve => server.once('exit', resolve)); }
    if (log !== undefined) fs.closeSync(log);
    fs.rmSync(directory, { recursive: true, force: true });
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
