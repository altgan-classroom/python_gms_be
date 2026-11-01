// Small DOM helpers. Pages build HTML strings; anything from the API goes through esc().

export const esc = (value) =>
  String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

export const $ = (selector, root = document) => root.querySelector(selector);

export const money = (n) => (n == null ? '' : `$${Number(n).toFixed(2)}`);

// en-CA formats as YYYY-MM-DD, which is what the services expect.
export const isoDate = (date) => date.toLocaleDateString('en-CA');
export const today = () => isoDate(new Date());
// Current wall-clock time at the gym, "YYYY-MM-DD HH:MM:SS". The services store gym-local times.
export const nowLocal = (location) =>
  new Date().toLocaleString('sv-SE', { timeZone: location?.location_time_info?.location_timezone }).slice(0, 19);

// Monday-to-Sunday dates of the week `offset` weeks from this one.
export function weekDays(offset = 0) {
  const monday = new Date();
  monday.setHours(0, 0, 0, 0);
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7) + offset * 7);
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    return d;
  });
}

export function table(columns, items, { empty = 'Nothing here yet.', rowAttrs = () => '' } = {}) {
  if (!items.length) return `<p class="empty">${esc(empty)}</p>`;
  const head = columns.map((c) => `<th>${esc(c.label)}</th>`).join('');
  const body = items
    .map((item) => `<tr ${rowAttrs(item)}>${columns.map((c) => `<td>${c.html ? c.html(item) : esc(item[c.key])}</td>`).join('')}</tr>`)
    .join('');
  return `<div class="table-wrap"><table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

export const options = (items, value, label, selected) =>
  items.map((i) => `<option value="${esc(i[value])}" ${i[value] == selected ? 'selected' : ''}>${esc(i[label])}</option>`).join('');

// Collects a form into a plain object: empty fields are dropped, number inputs become numbers,
// checkboxes become booleans, and a multi-select becomes an array of numbers.
export function formData(form) {
  const out = {};
  for (const el of form.elements) {
    if (!el.name) continue;
    if (el.type === 'checkbox') out[el.name] = el.checked;
    else if (el.multiple) out[el.name] = [...el.selectedOptions].map((o) => Number(o.value));
    else if (el.value === '') continue;
    else out[el.name] = el.type === 'number' || el.dataset.number !== undefined ? Number(el.value) : el.value;
  }
  return out;
}

// Opens a <dialog> with a form. onSubmit receives the form data; throwing keeps the dialog open
// and shows the message inside it.
export function openForm({ title, fields, submit, onSubmit }) {
  const dialog = document.createElement('dialog');
  dialog.innerHTML = `
    <form method="dialog" class="form">
      <h2>${esc(title)}</h2>
      ${fields}
      <p class="form-error" role="alert" hidden></p>
      <div class="actions">
        <button type="button" class="ghost" data-close>Cancel</button>
        <button type="submit">${esc(submit)}</button>
      </div>
    </form>`;
  document.body.append(dialog);
  const form = $('form', dialog);
  const error = $('.form-error', dialog);
  $('[data-close]', dialog).onclick = () => dialog.close();
  dialog.addEventListener('close', () => dialog.remove());
  form.onsubmit = async (event) => {
    event.preventDefault();
    const button = event.submitter;
    button.disabled = true;
    error.hidden = true;
    try {
      await onSubmit(formData(form), form);
      dialog.close();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    } finally {
      button.disabled = false;
    }
  };
  dialog.showModal();
  return dialog;
}

export const field = (label, input, hint = '') =>
  `<label class="field"><span>${esc(label)}</span>${input}${hint ? `<small>${esc(hint)}</small>` : ''}</label>`;

export function toast(message, kind = 'ok') {
  let region = $('.toasts');
  if (!region) {
    region = document.createElement('div');
    region.className = 'toasts';
    document.body.append(region);
  }
  const el = document.createElement('div');
  el.className = `toast ${kind}`;
  el.setAttribute('role', 'status');
  el.textContent = message;
  region.append(el);
  setTimeout(() => el.remove(), 4000);
}

// Runs an action from a button, reporting failures instead of leaving an unhandled rejection.
export async function run(action, success) {
  try {
    const result = await action();
    if (success) toast(success);
    return result;
  } catch (err) {
    toast(err.message, 'error');
  }
}
