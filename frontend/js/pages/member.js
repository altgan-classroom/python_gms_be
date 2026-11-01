import { session } from '../session.js';
import { rows } from '../api.js';
import { getMember, updateMemberProfile, listMemberships, createMembership, updateMembership, listInvoices } from '../services/members.js';
import { listPlans } from '../services/plans-classes.js';
import { MEMBERSHIP_STATUS } from '../lookups.js';
import { $, esc, table, field, openForm, options, money, today, toast, run } from '../ui.js';

export async function render(main, { id }) {
  const memberId = Number(id);
  const locationId = session.locationId;

  const [{ data: member }, memberships, invoices] = await Promise.all([
    getMember(locationId, memberId),
    listMemberships(locationId, memberId),
    listInvoices(locationId, memberId),
  ]);

  main.innerHTML = `
    <p><a href="#/members">Back to members</a></p>
    <header class="page-head">
      <div>
        <h1>${esc(member.first_name)} ${esc(member.last_name)}</h1>
        <p class="lede">
          <span class="pill pill-${esc(member.contact_type?.toLowerCase())}">${esc(member.contact_type)}</span>
          ${esc(member.membership_status ?? '')}, ${esc(member.payment_status ?? 'no payments')}
        </p>
      </div>
      <button class="ghost" id="edit-profile">Edit profile</button>
    </header>

    <section class="panel">
      <h2>Profile</h2>
      <dl class="facts">
        <dt>Email</dt><dd>${esc(member.email)}</dd>
        <dt>Phone</dt><dd>${esc(member.phone_number ?? 'None')}</dd>
        <dt>Birth date</dt><dd>${esc(member.birth_date ?? 'None')}</dd>
        <dt>Address</dt><dd>${esc([member.address_street, member.address_city, member.address_state, member.address_zip].filter(Boolean).join(', ') || 'None')}</dd>
        <dt>Balance</dt><dd>${money(member.outstanding_balance)}</dd>
        <dt>Member since</dt><dd>${esc(member.create_datetime)}</dd>
      </dl>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>Memberships</h2>
        <button class="small" id="add-membership">Sell a plan</button>
      </div>
      ${table(
        [
          { label: 'Plan', key: 'plan_name' },
          { label: 'Status', html: (m) => `<span class="pill pill-${esc(m.membership_status?.toLowerCase())}">${esc(m.membership_status)}</span>` },
          { label: 'Starts', key: 'start_date' },
          { label: 'Ends', key: 'end_date' },
          { label: 'Sessions', key: 'session_limits' },
          {
            label: '',
            html: (m) => (m.membership_status === 'Active' ? `<button class="ghost small" data-cancel="${m.membership_id}">Cancel membership</button>` : ''),
          },
        ],
        rows(memberships),
        { empty: 'No memberships. Sell a plan to create one.' },
      )}
    </section>

    <section class="panel">
      <h2>Invoices</h2>
      ${table(
        [
          { label: 'Created', key: 'created_date' },
          { label: 'Description', key: 'description' },
          { label: 'Amount', html: (i) => money(i.total_amount) },
          { label: 'Paid', html: (i) => (i.payments?.length ? 'Yes' : 'No') },
        ],
        rows(invoices),
        { empty: 'No invoices yet.' },
      )}
    </section>`;

  const reload = () => render(main, { id });
  $('#edit-profile').onclick = () => editProfileForm(member, reload);
  $('#add-membership').onclick = () => sellPlanForm(memberId, reload);
  for (const button of main.querySelectorAll('[data-cancel]')) {
    button.onclick = () =>
      run(async () => {
        await updateMembership(locationId, memberId, Number(button.dataset.cancel), {
          membership_status_type_id: MEMBERSHIP_STATUS.CANCELLED,
          cancel_date: today(),
        });
        await reload();
      }, 'Membership cancelled');
  }
}

function editProfileForm(member, reload) {
  const input = (name, type = 'text', extra = '') => `<input name="${name}" type="${type}" value="${esc(member[name] ?? '')}" ${extra}>`;
  openForm({
    title: 'Edit profile',
    submit: 'Save profile',
    fields: `
      <div class="row">
        ${field('First name', input('first_name', 'text', 'required'))}
        ${field('Last name', input('last_name', 'text', 'required'))}
      </div>
      ${field('Email', input('email', 'email', 'required'))}
      ${field('Phone', input('phone_number', 'tel'))}
      ${field('Birth date', input('birth_date', 'date'))}
      ${field('Street', input('address_street'))}
      <div class="row">
        ${field('City', input('address_city'))}
        ${field('State', input('address_state'))}
        ${field('ZIP', input('address_zip'))}
      </div>`,
    onSubmit: async (profile) => {
      await updateMemberProfile(session.locationId, member.member_id, profile);
      toast('Profile saved');
      await reload();
    },
  });
}

async function sellPlanForm(memberId, reload) {
  const plans = rows(await run(() => listPlans(session.locationId))).filter((p) => p.plan_status === 'Active');
  const dialog = openForm({
    title: 'Sell a plan',
    submit: 'Create membership',
    fields: `
      ${field('Plan', `<select name="plan_id" data-number required>${options(plans, 'plan_id', 'plan_name')}</select>`, 'Plans come from plans-classes-service. The membership is saved by members-service.')}
      ${field('Start date', `<input name="plan_start_date" type="date" required value="${today()}">`)}
      <button type="button" class="ghost small" data-preview>Preview charges</button>
      <div class="preview" aria-live="polite"></div>`,
    onSubmit: async (membership) => {
      // process=true saves the membership and its invoice. Payment is left for the front desk.
      await createMembership(session.locationId, memberId, membership, true);
      toast('Membership created');
      await reload();
    },
  });

  // Without process=true the endpoint only prices the membership (the backend still saves free plans here).
  $('[data-preview]', dialog).onclick = async () => {
    const form = $('form', dialog);
    const error = $('.form-error', dialog);
    const preview = $('.preview', dialog);
    error.hidden = true;
    preview.innerHTML = '';
    let data;
    try {
      ({ data } = await createMembership(session.locationId, memberId, {
        plan_id: Number(form.plan_id.value),
        plan_start_date: form.plan_start_date.value,
      }));
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
      return;
    }
    preview.innerHTML = data.free
      ? '<p>This plan is free.</p>'
      : `${table(
          [
            { label: 'Due', html: (p) => esc(p.due_date ?? 'At signup') },
            { label: 'Plan', html: (p) => money(p.plan_payment) },
            { label: 'Tax', html: (p) => money(p.tax) },
            { label: 'Total', html: (p) => money(p.total_amount) },
          ],
          data.payments ?? [],
        )}<p><strong>Total ${money(data.total_amount)}</strong></p>`;
  };
}
