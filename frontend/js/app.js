import { session } from './session.js';
import { mountInspector } from './inspector.js';
import { $, esc, options } from './ui.js';
import * as login from './pages/login.js';
import * as overview from './pages/overview.js';
import * as members from './pages/members.js';
import * as member from './pages/member.js';
import * as plans from './pages/plans.js';
import * as classes from './pages/classes.js';
import * as staff from './pages/staff.js';
import * as reports from './pages/reports.js';

// Hash routes: #/members/8985 matches /members/:id and passes { id: '8985' }.
const routes = [
  ['/login', login],
  ['/', overview],
  ['/members', members],
  ['/members/:id', member],
  ['/plans', plans],
  ['/classes', classes],
  ['/staff', staff],
  ['/reports', reports],
];

function match(path) {
  for (const [pattern, page] of routes) {
    const keys = [];
    const regex = new RegExp(`^${pattern.replace(/:(\w+)/g, (_, k) => (keys.push(k), '([^/]+)'))}$`);
    const found = path.match(regex);
    if (found) return { page, params: Object.fromEntries(keys.map((k, i) => [k, found[i + 1]])) };
  }
  return null;
}

async function route() {
  const path = location.hash.slice(1) || '/';
  const signedIn = Boolean(session.accessToken && session.user);
  if (!signedIn && path !== '/login') return (location.hash = '#/login');
  if (signedIn && path === '/login') return (location.hash = '#/');

  renderShell(signedIn);
  const main = $('#main');
  const found = match(path);
  if (!found) {
    main.innerHTML = '<h1>Page not found</h1><p><a href="#/">Go to the overview</a></p>';
    return;
  }
  for (const a of document.querySelectorAll('.nav a')) {
    const target = a.getAttribute('href').slice(1);
    a.toggleAttribute('aria-current', target === '/' ? path === '/' : path.startsWith(target));
  }
  // A fresh container per visit: if the user navigates away mid-load, the late render lands in a
  // detached element instead of overwriting the next page.
  const view = document.createElement('div');
  view.className = 'view';
  view.innerHTML = '<p class="loading">Loading…</p>';
  main.replaceChildren(view);
  try {
    await found.page.render(view, found.params);
  } catch (err) {
    view.innerHTML = `<h1>Could not load this page</h1><p class="form-error">${esc(err.message)}</p>`;
  }
  main.focus({ preventScroll: true });
}

function renderShell(signedIn) {
  $('.sidebar').hidden = !signedIn;
  document.body.classList.toggle('signed-out', !signedIn);
  if (!signedIn) return;
  const locations = session.user.locations || [];
  $('#location').innerHTML = options(locations, 'location_id', 'name', session.locationId);
  const profile = session.user.user_profile;
  $('#user-name').textContent = profile ? `${profile.first_name} ${profile.last_name}` : session.user.email;
  $('#user-role').textContent = session.user.role?.name ?? '';
}

$('#location').onchange = (e) => {
  session.save({ locationId: Number(e.target.value) });
  route();
};

$('#sign-out').onclick = () => {
  session.clear();
  location.hash = '#/login';
};

$('#inspector-toggle').onclick = (e) => {
  const open = document.body.classList.toggle('inspector-open');
  e.currentTarget.setAttribute('aria-expanded', open);
};

mountInspector($('#inspector'));
window.addEventListener('hashchange', route);
route();
