// The network panel: every call made through api() lands here with its request and response.
import { onCall, OK } from './api.js';
import { SERVICES } from './config.js';
import { esc, $, toast } from './ui.js';

const calls = new Map();
let panel;

export function mountInspector(root) {
  panel = root;
  panel.innerHTML = `
    <header class="inspector-head">
      <h2>Network</h2>
      <span class="count" aria-live="polite"></span>
      <button class="ghost small" data-clear>Clear</button>
    </header>
    <p class="inspector-hint">Each row is one HTTP call from this page to a backend container. Open a row to see the full request and response.</p>
    <ol class="calls"></ol>`;
  $('[data-clear]', panel).onclick = () => {
    calls.clear();
    $('.calls', panel).innerHTML = '';
    updateCount();
  };
  onCall(render);
}

function render(call) {
  let item = calls.get(call.id);
  if (!item) {
    item = document.createElement('li');
    item.innerHTML = '<details><summary></summary><div class="call-body"></div></details>';
    calls.set(call.id, item);
    $('.calls', panel).prepend(item);
    updateCount();
  }
  const svc = SERVICES[call.service];
  const url = new URL(call.url);
  const envelope = call.response?.status;
  const state = call.failed ? 'fail' : call.httpStatus === undefined ? 'pending' : isOk(call) ? 'ok' : 'fail';

  item.className = `call ${state}`;
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
  $('.count', panel).textContent = `${calls.size} call${calls.size === 1 ? '' : 's'}`;
}
