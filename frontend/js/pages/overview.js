import { session } from '../session.js';
import { rows } from '../api.js';
import { listStaff } from '../services/auth-admin.js';
import { listMembers } from '../services/members.js';
import { listPlans, listClasses } from '../services/plans-classes.js';
import { getReport } from '../services/reports.js';
import { esc, isoDate, weekDays } from '../ui.js';

export async function render(main) {
  const id = session.locationId;
  const week = weekDays();
  const started = performance.now();

  // One page, four services, fired together. The slowest one sets the load time.
  const tiles = [
    { label: 'Contacts', service: 'members', load: () => listMembers(id).then((r) => rows(r).length) },
    { label: 'Plans on sale', service: 'plans', load: () => listPlans(id).then((r) => rows(r).filter((p) => p.plan_status === 'Active').length) },
    {
      label: 'Classes this week',
      service: 'plans',
      load: () => listClasses(id, `${isoDate(week[0])} 00:00:00`, `${isoDate(week[6])} 23:59:59`).then((r) => r.data?.classes?.length ?? 0),
    },
    { label: 'Staff', service: 'auth', load: () => listStaff(id).then((r) => rows(r).length) },
    { label: 'Full members', service: 'reports', load: () => getReport(id, 'LOCMEMBCOUNT').then((r) => r.data?.reports?.[0]?.full_members ?? 0) },
  ];
  const results = await Promise.allSettled(tiles.map((t) => t.load()));
  const elapsed = Math.round(performance.now() - started);

  main.innerHTML = `
    <header class="page-head">
      <div>
        <h1>${esc(session.location?.name ?? 'Overview')}</h1>
        <p class="lede">${esc([session.location?.city, session.location?.state].filter(Boolean).join(', '))}</p>
      </div>
    </header>
    <p class="fanout">This page made ${tiles.length} requests to 4 services at the same time and finished in ${elapsed} ms.</p>
    <ul class="tiles">
      ${tiles
        .map((t, i) => {
          const r = results[i];
          return `
            <li class="tile svc-edge-${t.service}">
              <span class="tile-value">${r.status === 'fulfilled' ? esc(r.value) : 'n/a'}</span>
              <span class="tile-label">${esc(t.label)}</span>
              <span class="tile-source svc-text-${t.service}">${r.status === 'fulfilled' ? '' : `${esc(r.reason.message)}<br>`}from ${esc(serviceName(t.service))}</span>
            </li>`;
        })
        .join('')}
    </ul>
    <section class="explain">
      <h2>Where the data lives</h2>
      <table class="map">
        <tbody>
          <tr><th class="svc-text-auth">auth-admin-service :5004</th><td>Sign-in, tokens, locations, rooms, staff</td></tr>
          <tr><th class="svc-text-members">members-service :5005</th><td>Members, memberships, invoices</td></tr>
          <tr><th class="svc-text-plans">plans-classes-service :5006</th><td>Plans, class schedule, bookings</td></tr>
          <tr><th class="svc-text-reports">reports-service :5008</th><td>Read-only reports over the shared database</td></tr>
        </tbody>
      </table>
    </section>`;
}

const serviceName = (key) => ({ auth: 'auth-admin', members: 'members', plans: 'plans-classes', reports: 'reports' })[key];
