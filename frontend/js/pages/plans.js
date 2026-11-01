import { session } from '../session.js';
import { rows } from '../api.js';
import { listPlans, createPlan, getPlan, updatePlan, deletePlan, listAccessGroups } from '../services/plans-classes.js';
import { BILLING_TYPES, DURATION_TYPES, MEMBERSHIP_TYPES } from '../lookups.js';
import { $, esc, table, field, openForm, options, money, toast, run } from '../ui.js';

export async function render(main) {
  const locationId = session.locationId;
  const [plans, groups] = await Promise.all([listPlans(locationId), listAccessGroups(locationId)]);
  const showRetired = main.dataset.showRetired === 'true';
  const list = rows(plans).filter((p) => showRetired || p.plan_status !== 'Cancelled');

  main.innerHTML = `
    <header class="page-head">
      <div>
        <h1>Plans</h1>
        <p class="lede">What members can buy. Classes are open to a plan through its access groups.</p>
      </div>
      <button id="add-plan">Add plan</button>
    </header>
    <label class="check"><input type="checkbox" id="show-retired" ${showRetired ? 'checked' : ''}> Show retired plans</label>
    ${table(
      [
        { label: 'Plan', key: 'plan_name' },
        { label: 'Billing', html: (p) => `${esc(p.billing_type)}<br><span class="muted small">${esc(p.plan_duration)}</span>` },
        { label: 'Price', html: (p) => money(p.price) },
        { label: 'Members', key: 'member_count' },
        { label: 'Access groups', html: (p) => esc(groupNames(rows(groups), p.class_access_group)) },
        { label: 'Status', html: (p) => `<span class="pill pill-${esc(p.plan_status?.toLowerCase())}">${esc(p.plan_status)}</span>` },
        {
          label: '',
          html: (p) =>
            p.plan_status === 'Cancelled'
              ? ''
              : `<span class="row-actions">
                   <button class="ghost small" data-access="${p.plan_id}">Access</button>
                   <button class="ghost small danger" data-retire="${p.plan_id}">Retire</button>
                 </span>`,
        },
      ],
      list,
      { empty: 'No plans yet. Add one so members have something to buy.' },
    )}`;

  const reload = () => render(main);
  $('#show-retired').onchange = (e) => {
    main.dataset.showRetired = e.target.checked;
    reload();
  };
  $('#add-plan').onclick = () => addPlanForm(reload);
  for (const b of main.querySelectorAll('[data-retire]')) {
    b.onclick = () =>
      run(async () => {
        await deletePlan(locationId, Number(b.dataset.retire));
        await reload();
      }, 'Plan retired');
  }
  for (const b of main.querySelectorAll('[data-access]')) {
    b.onclick = () => accessForm(Number(b.dataset.access), rows(groups), reload);
  }
}

const groupNames = (groups, ids) =>
  (ids ?? []).map((id) => groups.find((g) => g.id === id)?.name ?? `#${id}`).join(', ') || 'None';

// Each billing type keeps its price in a different field.
const PRICE_FIELD = { 1: 'recurring_amount', 2: 'paid_in_full_price', 3: 'class_or_session_pack_price' };

function addPlanForm(reload) {
  openForm({
    title: 'Add plan',
    submit: 'Add plan',
    fields: `
      ${field('Name', '<input name="name" required>')}
      ${field('Description', '<input name="description">')}
      <div class="row">
        ${field('Billing', `<select name="billing_type_id" data-number>${options(BILLING_TYPES, 'id', 'name', 2)}</select>`)}
        ${field('Price', '<input name="price" type="number" min="0" step="0.01" value="0">', 'Per billing period for recurring plans')}
      </div>
      <div class="row">
        ${field('Length', '<input name="duration" type="number" min="1" value="1" required>')}
        ${field('Unit', `<select name="duration_type_id" data-number>${options(DURATION_TYPES, 'id', 'name', 3)}</select>`)}
      </div>
      <div class="row">
        ${field('Type', `<select name="membership_type_id" data-number>${options(MEMBERSHIP_TYPES, 'id', 'name', 1)}</select>`)}
        ${field('Sessions in pack', '<input name="sessions_count" type="number" min="1">', 'Session packs only')}
      </div>
      <label class="check"><input type="checkbox" name="auto_renewal"> Renews automatically</label>`,
    onSubmit: async ({ price, ...form }) => {
      const plan = { description: null, plan_status_type_id: 1, ...form };
      if (PRICE_FIELD[form.billing_type_id]) plan[PRICE_FIELD[form.billing_type_id]] = price;
      if (form.billing_type_id === 1) Object.assign(plan, { recurring_interval: 1, recurring_duration_type_id: 3, unlimited: true });
      await createPlan(session.locationId, plan);
      toast(`${form.name} added`);
      await reload();
    },
  });
}

async function accessForm(planId, groups, reload) {
  const { data: plan } = await run(() => getPlan(session.locationId, planId));
  if (!groups.length) return toast('Create an access group on the Classes page first.', 'error');
  openForm({
    title: `Access for ${plan.name}`,
    submit: 'Save access',
    fields: `
      <p class="muted">Members on this plan can book classes in the groups you tick.</p>
      ${groups
        .map((g) => `<label class="check"><input type="checkbox" name="group-${g.id}" ${plan.class_access_groups.includes(g.id) ? 'checked' : ''}> ${esc(g.name)}</label>`)
        .join('')}`,
    onSubmit: async (form) => {
      const class_access_groups = groups.filter((g) => form[`group-${g.id}`]).map((g) => g.id);
      // Plans created elsewhere can have a null status, which the PUT validator rejects.
      await updatePlan(session.locationId, { ...plan, plan_status_type_id: plan.plan_status_type_id ?? 1, class_access_groups });
      toast('Access saved');
      await reload();
    },
  });
}
