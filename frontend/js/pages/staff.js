import { session } from '../session.js';
import { rows } from '../api.js';
import { listStaff, createStaff } from '../services/auth-admin.js';
import { ROLE_TYPES } from '../lookups.js';
import { $, esc, table, field, openForm, options, toast } from '../ui.js';

export async function render(main) {
  const staff = rows(await listStaff(session.locationId));

  main.innerHTML = `
    <header class="page-head">
      <div>
        <h1>Staff</h1>
        <p class="lede">People who can sign in to this console. Staff accounts are users in auth-admin-service.</p>
      </div>
      <button id="add-staff">Add staff</button>
    </header>
    ${table(
      [
        { label: 'Name', html: (u) => `${esc(u.first_name)} ${esc(u.last_name)}` },
        { label: 'Role', html: (u) => `<span class="pill">${esc(u.staff_member_role)}</span>` },
        { label: 'Email', key: 'email' },
        { label: 'Verified', html: (u) => (u.verified_on ? 'Yes' : 'Not yet') },
        { label: 'Added', key: 'create_datetime' },
      ],
      staff,
    )}`;

  $('#add-staff').onclick = () =>
    openForm({
      title: 'Add staff',
      submit: 'Add staff',
      fields: `
        <div class="row">
          ${field('First name', '<input name="first_name" required>')}
          ${field('Last name', '<input name="last_name" required>')}
        </div>
        ${field('Email', '<input name="email" type="email" required>')}
        ${field('Phone', '<input name="phone_number" type="tel">')}
        ${field('Role', `<select name="role_type_id" data-number>${options(ROLE_TYPES, 'id', 'name', 5)}</select>`)}
        <p class="muted">New accounts get the password Test@1234, so you can sign in as them straight away.</p>`,
      onSubmit: async (user) => {
        await createStaff(session.locationId, user);
        toast(`${user.first_name} ${user.last_name} added`);
        await render(main);
      },
    });
}
