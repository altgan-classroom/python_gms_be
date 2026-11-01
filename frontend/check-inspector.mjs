// One runnable check for the network panel's grouping: node frontend/check-inspector.mjs
// Serves the frontend, drives it in headless Chrome over CDP, asserts calls land under the
// action that caused them. Needs no backend: fetch is stubbed inside the page.
import { spawn } from 'node:child_process';
import assert from 'node:assert';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 8899;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const server = spawn('python3', ['-m', 'http.server', PORT], { cwd: import.meta.dirname, stdio: 'ignore' });
const chrome = spawn(CHROME, ['--headless=new', '--remote-debugging-port=9333', '--no-first-run', '--user-data-dir=/tmp/gms-cdp', 'about:blank'], { stdio: 'ignore' });

let ws, id = 0;
const pending = new Map();
const cdp = (method, params = {}) =>
  new Promise((res, rej) => (pending.set(++id, { res, rej }), ws.send(JSON.stringify({ id, method, params }))));

async function evaluate(expression) {
  const r = await cdp('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
  return r.result.value;
}

const readGroups = () =>
  evaluate(`[...document.querySelectorAll('.group')].map(g => ({
    cls: g.className, act: g.querySelector('.act').textContent,
    tally: g.querySelector('.tally').textContent, calls: g.querySelectorAll('.call').length }))`);

// Every endpoint answers with one envelope that satisfies login, /me and the overview.
const STUB = `window.fetch = async () => new Response(JSON.stringify({ status: 'SUCCESS', data: {
  access_token: 'a.b.c', refresh_token: 'r', email: 'owner@demo.gym', user_profile: null, role: { name: 'Owner' },
  locations: [{ location_id: 1, name: 'Demo gym', primary: true }] } }), { status: 200 });`;

try {
  let targets;
  for (let i = 0; i < 40; i++) {
    try { targets = await (await fetch('http://localhost:9333/json')).json(); break; } catch { await sleep(250); }
  }
  ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    const p = pending.get(m.id);
    if (!p) return;
    pending.delete(m.id);
    m.error ? p.rej(new Error(m.error.message)) : p.res(m.result);
  };

  await cdp('Page.enable');
  await cdp('Page.addScriptToEvaluateOnNewDocument', { source: `localStorage.clear(); ${STUB}` });
  await cdp('Page.navigate', { url: `http://localhost:${PORT}/index.html` });
  await sleep(1500);

  assert.equal(await readGroups().then((g) => g.length), 0, 'no calls yet, so no groups');

  await evaluate("document.querySelector('.login button[type=submit]').click()");
  await sleep(1200);

  const groups = await readGroups();
  const count = await evaluate("document.querySelector('.inspector .count').textContent");
  console.log(JSON.stringify({ groups, count }, null, 2));

  const signIn = groups.find((g) => g.act === 'Submit “Sign in”');
  assert.ok(signIn, 'the submit is a group of its own');
  assert.equal(signIn.calls, 2, 'both calls the sign-in makes sit under it');
  assert.ok(signIn.cls.includes('ok') && signIn.tally.startsWith('2 calls'), signIn.tally);
  assert.ok(groups.some((g) => g.act.startsWith('Go to #/')), 'the route change opens its own group');
  assert.equal(groups.length, 2, 'two actions, two groups');
  assert.match(count, /^\d+ calls in 2 actions$/);
  console.log('OK');
} finally {
  ws?.close();
  chrome.kill();
  server.kill();
}
