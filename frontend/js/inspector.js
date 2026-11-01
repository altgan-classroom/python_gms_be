// The network panel: every call made through api() lands here with its request and response.
// Calls are grouped by the thing the user did — a click, a form submit, a page change —
// so a row of 4 calls reads as "this is what pressing Save costs".
import { onCall, OK } from './api.js';
import { SERVICES } from './config.js';
import { esc, $, toast } from './ui.js';

const calls = new Map();
let panel, groupList, activity, group;

export function mountInspector(root) {
  panel = root;
  panel.innerHTML = `
    <header class="inspector-head">
      <h2>Network</h2>
      <span class="count" aria-live="polite"></span>
      <button class="ghost small" data-clear>Clear</button>
    </header>
    <p class="inspector-hint">Calls are grouped by what you did. Open a group to see its HTTP calls, open a call to see the full request and response.</p>
    <ol class="groups"></ol>`;
  groupList = $('.groups', panel);
  $('[data-clear]', panel).onclick = () => {
    calls.clear();
    groupList.innerHTML = '';
    group = null;
    updateCount();
  };
  onCall(render);

  // Capture phase: we see the gesture before the page's own handler fires the call.
  addEventListener('click', onGesture, true);
  addEventListener('submit', onGesture, true);
  addEventListener('change', onGesture, true);
  addEventListener('hashchange', () => start(`Go to ${location.hash || '#/'}`));
  start('Page load');
}

function onGesture(event) {
  if (panel.contains(event.target)) return;
  start(describe(event));
}

// A gesture only names the next group; the group appears when its first call does, so
// clicking something that talks to nobody leaves the panel alone.
function start(name) {
  activity = { name, at: new Date() };
  group = null;
}

const CONTROL = /^(INPUT|SELECT|TEXTAREA)$/;

function describe(event) {
  const verb = event.type === 'submit' ? 'Submit' : event.type === 'change' ? 'Change' : 'Click';
  const el = event.submitter || event.target.closest('button, a, [role="button"], input, select, textarea, tr');
  if (!el) return `${verb} ${event.target.tagName.toLowerCase()}`;
  const name =
    el.getAttribute('aria-label') ||
    (CONTROL.test(el.tagName) ? el.labels?.[0]?.textContent || el.name : el.textContent) ||
    el.value ||
    el.tagName;
  const text = name.trim().replace(/\s+/g, ' ');
  return `${verb} ${text ? `“${text.slice(0, 48)}”` : el.tagName.toLowerCase()}`;
}

function openGroup() {
  if (group) return group;
  const previous = groupList.firstElementChild;
  if (previous) $('details', previous).open = false;

  const li = document.createElement('li');
  li.className = 'group pending';
  li.innerHTML = `<details open>
      <summary><span class="act"></span><span class="when"></span><span class="tally"></span></summary>
      <ol class="calls"></ol>
    </details>`;
  $('.act', li).textContent = activity.name;
  $('.when', li).textContent = activity.at.toLocaleTimeString();
  groupList.prepend(li);
  group = { el: li, list: $('.calls', li), calls: [] };
  return group;
}

function render(call) {
  let entry = calls.get(call.id);
  if (!entry) {
    const item = document.createElement('li');
    item.innerHTML = '<details><summary></summary><div class="call-body"></div></details>';
    entry = { item, group: openGroup() };
    entry.group.calls.push(call);
    entry.group.list.append(item);
    calls.set(call.id, entry);
    updateCount();
  }
  renderCall(call, entry.item);
  renderGroup(entry.group);
}

function renderCall(call, item) {
  const svc = SERVICES[call.service];
  const url = new URL(call.url);
  const envelope = call.response?.status;

  item.className = `call ${state(call)}`;
  $('summary', item).innerHTML = `
    <span class="method m-${call.method.toLowerCase()}">${call.method}</span>
    <span class="svc svc-${call.service}" title="${esc(svc.name)}">:${svc.port}</span>
    <span class="path">${esc(url.pathname)}${esc(url.search)}</span>
    <span class="status">${call.failed ? 'no answer' : call.httpStatus === undefined ? '…' : `${call.httpStatus}${envelope ? ` ${esc(envelope)}` : ''}`}</span>
    <span class="ms">${call.ms ? `${Math.round(call.ms)} ms` : ''}</span>`;

  const body = $('.call-body', item);
  body.innerHTML = `
    <dl>
      <dt>Service</dt><dd>${esc(svc.name)} <span class="muted">(container port ${svc.port})</span></dd>
      <dt>URL</dt><dd class="mono">${esc(call.url)}</dd>
    </dl>
    <h3>Request headers</h3>
    <pre>${esc(json(maskHeaders(call.headers)))}</pre>
    ${call.body !== undefined ? `<h3>Request body</h3><pre>${esc(json(call.body))}</pre>` : ''}
    <h3>Response</h3>
    <pre>${call.failed ? 'The container did not answer. Is it running?' : esc(json(call.response))}</pre>
    <button class="ghost small" data-curl>Copy as curl</button>`;
  $('[data-curl]', body).onclick = () =>
    navigator.clipboard.writeText(curl(call)).then(() => toast('curl command copied'), () => toast('Clipboard is blocked in this browser', 'error'));
}

function renderGroup({ el, calls: group }) {
  const states = group.map(state);
  const failed = states.filter((s) => s === 'fail').length;
  el.className = `group ${states.includes('pending') ? 'pending' : failed ? 'fail' : 'ok'}`;
  // Wall clock across the group, not the sum: calls fired together cost one wait, not two.
  const done = group.filter((c) => c.ms);
  const span = done.length ? Math.max(...done.map((c) => c.started + c.ms)) - Math.min(...group.map((c) => c.started)) : 0;
  $('.tally', el).textContent = [
    `${group.length} call${group.length === 1 ? '' : 's'}`,
    span ? `${Math.round(span)} ms` : '…',
    failed ? `${failed} failed` : '',
  ]
    .filter(Boolean)
    .join(' · ');
}

const state = (call) => (call.failed ? 'fail' : call.httpStatus === undefined ? 'pending' : isOk(call) ? 'ok' : 'fail');

const isOk = (call) => call.httpStatus < 400 && OK.has(call.response?.status);

const json = (value) => JSON.stringify(value, null, 2) ?? '';

function maskHeaders(headers) {
  const auth = headers.Authorization;
  return auth ? { ...headers, Authorization: `${auth.slice(0, 20)}…${auth.slice(-6)}` } : headers;
}

function curl(call) {
  const parts = [`curl -X ${call.method} '${call.url}'`];
  for (const [k, v] of Object.entries(call.headers)) parts.push(`-H '${k}: ${v}'`);
  if (call.body !== undefined) parts.push(`-d '${JSON.stringify(call.body)}'`);
  return parts.join(' \\\n  ');
}

function updateCount() {
  const actions = groupList.childElementCount;
  $('.count', panel).textContent = `${calls.size} call${calls.size === 1 ? '' : 's'} in ${actions} action${actions === 1 ? '' : 's'}`;
}
