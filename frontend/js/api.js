import { SERVICES } from './config.js';
import { session } from './session.js';

// Every service replies with the same envelope: { status, message, data }.
// These statuses mean the call worked. NOT_FOUND is "worked, nothing there" for list endpoints.
export const OK = new Set(['SUCCESS', 'FOUND', 'CREATED', 'UPDATED', 'DELETED', 'SAVED', 'NOT_FOUND']);

export class ApiError extends Error {}

const listeners = new Set();
export const onCall = (fn) => listeners.add(fn);
const emit = (call) => listeners.forEach((fn) => fn(call));
let seq = 0;

export async function api(service, method, path, { query, body, auth = true } = {}, retried = false) {
  const svc = SERVICES[service];
  const url = new URL(svc.base + path);
  for (const [k, v] of Object.entries(query || {})) {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v);
  }

  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (auth && session.accessToken) headers.Authorization = `Bearer ${session.accessToken}`;

  const call = { id: ++seq, service, method, url: url.toString(), headers, body, started: performance.now() };
  emit(call);

  let res, json;
  try {
    res = await fetch(url, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
    json = await res.json().catch(() => null);
  } catch {
    Object.assign(call, { failed: true, ms: performance.now() - call.started });
    emit(call);
    throw new ApiError(`${svc.name} did not answer on port ${svc.port}. Start it with: docker compose up -d ${svc.name}`);
  }
  Object.assign(call, { httpStatus: res.status, response: json, ms: performance.now() - call.started });
  emit(call);

  // An expired access token comes back as HTTP 200 with status UNAUTHORIZED, not as a 401.
  if (json?.status === 'UNAUTHORIZED' && auth && session.refreshToken && !retried) {
    if (await refreshAccessToken()) return api(service, method, path, { query, body, auth }, true);
    session.clear();
    location.hash = '#/login';
  }

  if (!res.ok || !OK.has(json?.status)) throw new ApiError(errorText(json, res));
  return json;
}

async function refreshAccessToken() {
  try {
    const json = await api('auth', 'POST', '/auth/refresh', { body: { refresh_token: session.refreshToken }, auth: false }, true);
    session.save({ accessToken: json.data.access_token });
    return true;
  } catch {
    return false;
  }
}

// FastAPI's own 422 validation errors use { detail: [...] } instead of the envelope.
function errorText(json, res) {
  if (Array.isArray(json?.detail)) {
    return json.detail.map((d) => `${d.loc.slice(1).join('.')}: ${d.msg}`).join('\n');
  }
  return json?.message || json?.detail || `HTTP ${res.status}`;
}

// List endpoints return data: {} instead of [] when nothing matches.
export const rows = (json) => (Array.isArray(json?.data) ? json.data : []);
