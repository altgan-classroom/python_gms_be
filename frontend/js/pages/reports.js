import { session } from '../session.js';
import { getReport } from '../services/reports.js';
import { REPORTS } from '../lookups.js';
import { $, esc, table, field, isoDate, today, toast } from '../ui.js';

export async function render(main) {
  const yearAgo = new Date();
  yearAgo.setFullYear(yearAgo.getFullYear() - 1);
  const groups = [...new Set(REPORTS.map((r) => r.service))];

  main.innerHTML = `
    <header class="page-head">
      <div>
        <h1>Reports</h1>
        <p class="lede">One endpoint in reports-service. The report name is part of the URL.</p>
      </div>
    </header>
    <form class="inline-form" id="report-form">
      ${field(
        'Report',
        `<select name="report">${groups
          .map((g) => `<optgroup label="${esc(g)}">${REPORTS.filter((r) => r.service === g).map((r) => `<option value="${r.id}">${esc(r.name)}</option>`).join('')}</optgroup>`)
          .join('')}</select>`,
      )}
      ${field('From', `<input name="from" type="date" value="${isoDate(yearAgo)}">`)}
      ${field('To', `<input name="to" type="date" value="${today()}">`)}
      <button type="submit">Run report</button>
    </form>
    <section id="report" aria-live="polite"></section>`;

  const form = $('#report-form');
  const out = $('#report');
  const run = async () => {
    out.innerHTML = '<p class="loading">Running…</p>';
    try {
      const json = await getReport(session.locationId, form.report.value, form.from.value, form.to.value);
      const data = json.data?.reports ?? [];
      const columns = Object.keys(data[0] ?? {}).map((key) => ({ label: key.replaceAll('_', ' '), key }));
      out.innerHTML = `
        <p class="muted">${esc(json.message)}</p>
        ${table(columns, data, { empty: 'No rows for this date range.' })}`;
    } catch (err) {
      out.innerHTML = '';
      toast(err.message, 'error');
    }
  };
  form.onsubmit = (e) => {
    e.preventDefault();
    run();
  };
  await run();
}
